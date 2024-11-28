// creating a video element and customizing it and append it to videos container
const local_video = document.getElementById('me');
local_video.autoplay = true;
const videosContainer = document.getElementById('videos')
videosContainer.appendChild(local_video)
const me = document.getElementById("username").textContent
const myId = document.getElementById("user-id").textContent

//STUN
var configuration = {
    "iceServers": [
        {
            "urls": "stun:stun.1.google.com:19302"
        },
        {
            urls: 'turn:192.158.29.39:3478?transport=tcp',
            credential: 'JZEOEt2V3Qb0y27GRntt2u2PAYA=',
            username: '28224511:1379330808'
        }
    ]
};


// getting user media
var localStream;
const constranits = { 'video': true, 'audio': false }

navigator.mediaDevices.getUserMedia(constranits).then(stream => {
    localStream = stream
    let peers = {};
    let callOwner = "nobody"
    local_video.srcObject = stream;

    // making the url of call consumer
    const course_id = JSON.parse(document.getElementById('course-id').textContent)
    const url = "ws://" + window.location.host + "/ws/call/room/" + course_id + "/"
    const websoc = new WebSocket(url)
    let peersCounter = 0
    // receving the answer and handling it with appropriate method
    websoc.onmessage = async (event) => {
        const data = JSON.parse(event.data)
        const type = data.type
        if (type == 'joined') {
            peersCounter += 1
            // IF I am joining
            if (peersCounter == 1) {
                websoc.send(JSON.stringify({ "type": "callOwner", "owner": makeKey(me, myId) }))
                const peerConnection = createPeer(makeKey(me, myId), "yes") // create a peer connection and send my offer
                localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream))
            }
        }
        else if (type == 'left') {
            console.log(callOwner, makeKey(me, myId))
            if (callOwner == makeKey(me, myId)) {
                websoc.send(JSON.stringify({ "type": "callEnd" }))
            }

            else if (type == "callEnd") {
                console.log("call end")
                videosContainer.style.display = "none"
            }

        }
        else if (type == 'offer') {
            // this offer is only processed by call Owner, and if he accepts, the offer and user name will be sent to other members
            const sender = data.senderName
            const offer = data.hisOffer
            console.log("offer came from-----------", sender)
            console.log(callOwner == makeKey(me, myId), sender != makeKey(me, myId))
            if (callOwner == makeKey(me, myId) && sender != makeKey(me, myId)) {
                console.log("new user offered an I am the owner")
                const new_user_btn = document.createElement("button")
                new_user_btn.innerText = "Allow" + sender.split("-")[0]
                new_user_btn.id = "Allow" + sender.split("-")[0]
                // offer came which i haven't send and I am the owner of the call to give permission
                document.getElementById("peers").appendChild(new_user_btn)
                document.getElementById(`Allow${sender.split("-")[0]}`).addEventListener("click", async (event) => {
                    const peerConnection = createPeer(sender, "no")
                    localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream))
                    console.log("sending this offer to otehr people-------", offer)
                    websoc.send(JSON.stringify({ "type": "memberAllowed", "member": sender, "hisOffer": offer }))
                    await handleOffer(sender, offer)
                })
            }

        }
        else if (type == "answer") {
            await answerd(data)
        }
        else if (type == "candidate") {
            await handleCandidate(data)
        }
        else if (type == "memberAllowed") {
            if (makeKey(me, myId) != callOwner) {
                // this state is for normal members of the call, so that add the new memeber to peers dict of every one
                const peerConnection = createPeer(data.member, "no")
                localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream))
                handleOffer(data.member, data["hisOffer"])
            }
        }
        else if (type == "callOwner") {
            callOwner = data.owner
            console.log("owner set", callOwner, data.senderName != makeKey(me, myId))
        }
    }


    async function sendOffer() {
        // creating offer and a local description
        peerConnection = peers[makeKey(me, myId)]
        const offer = await peerConnection.createOffer();
        peerConnection.setLocalDescription(offer)
        websoc.send(JSON.stringify({ "type": "offer", 'offer': offer, 'senderName': makeKey(me, myId) }))
        console.log("this is the offer I have sent", offer)
    }

    async function handleOffer(sender, offer) {
        // creating a peer connection, when an offer comes
        peerConnection = peers[sender]
        console.log("answering to........", sender, "<<<< peers dict---", peers, "<<<< me:---", makeKey(me, myId))
        console.log("data of offer came", offer)

        if (peerConnection) {
            await peerConnection.setRemoteDescription(new RTCSessionDescription(offer))
            // sending the answer back accoding to offer
            const answer = await peerConnection.createAnswer()
            await peerConnection.setLocalDescription(answer)
            console.log("answer send....")
            websoc.send(JSON.stringify({ "type": 'answer', 'answer': answer, "senderName": makeKey(me, myId), "hisOffer": offer }))
        }
    }

    async function answerd(data) {
        const sender = data["senderName"]
        let peerConnection = peers[sender] // 
        console.log("peer answerd ........his data", data, "<<<< peers dict---", peers, "<<<< me:---", makeKey(me, myId))
        console.log("my shared offer to all after perm...", data["hisOffer"])

        if (data["senderName"] != callOwner && data["senderName"] != makeKey(me, myId)) {
            // agar in bande khoda fekr mekona in answer naaq amada
            peerConnection = createPeer(data["senderName"], "no")
            localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream))
            const myGuessOffer = data["hisOffer"]
            await peerConnection.createOffer()
            await peerConnection.setLocalDescription(myGuessOffer)
            console.log('local description set for mashkokk!', sender)
        }

        await peerConnection.setRemoteDescription(new RTCSessionDescription(data.answer));

    }

    async function handleCandidate(data) {
        if (data["senderName"] != makeKey(me, myId)) {
            console.log("candidate came from.......", data["senderName"], "<<<< peers", peers)
            let peerConnection = peers[data["senderName"]] // 
            console.log(peerConnection, "peer connection found in ice candidate....")
            await peerConnection.addIceCandidate(new RTCIceCandidate(data.candidate));
        }
    }

    function createPeer(user, sendAnOffer) {
        let peerConnection = new RTCPeerConnection(configuration)

        // handling any tracks to this RTC party
        peerConnection.ontrack = (event) => {
            const pair_video = document.createElement('video');
            pair_video.autoplay = true;
            pair_video.srcObject = event.streams[0];
            videosContainer.appendChild(pair_video)
        }
        const sentCandidates = new Set()
        //  Ice candidates comming to this RTC party 
        peerConnection.onicecandidate = (event) => {
            if (event.candidate && !sentCandidates.has(event.candidate)) {
                websoc.send(JSON.stringify({ "type": "candidate", 'candidate': event.candidate, "senderName": user }))
                sentCandidates.add(event.candidate)
            }
        };
        peers[user] = peerConnection
        if (sendAnOffer == "yes") {
            sendOffer();
        }
        return peerConnection

    }

    function makeKey(user, id) {
        return user + "-" + id
    }


}).catch(error => {
    console.log('error in acheving access to media', error)
})

