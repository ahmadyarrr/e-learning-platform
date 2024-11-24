// creating a video element and customizing it and append it to videos container
const local_video = document.getElementById('me');
local_video.autoplay = true;
const videosContainer = document.getElementById('videos')
videosContainer.appendChild(local_video)
const me = document.getElementById("username").textContent
const myId = document.getElementById("user-id").textContent

// getting user media
var localStream;
const constranits = { 'video': true, 'audio': true }

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
                window.alert("owner sent")
            }
        }
        else if (type == 'left') {
            console.log('user left---')
            websoc.send(JSON.stringify({ "type": "call-end" }))
        }
        else if (type == 'offer') {
            console.log("++++++++++++++++++++++++++++")

            const owner = data.callOwner
            const sender = data.sender
            const offer = data.offer
            console.log("offer came...", owner, sender)
            if (owner == makeKey(me, myId) && data.sender != makeKey(me, myId)) {
                console.log("I am the call owner and request came to me")
                document.getElementById("peers").innerHTML += `<button type="button" id="Allow${sender.split("-")[0]}" >Allow${sender}</button>`
                document.getElementById(`call${user}`).addEventListener("click", async (event) => {
                    const peerConnection = createPeer(sender, "no")
                    localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream))
                    websoc.send(JSON.stringify({ "type": "memberAllowed", "sender": sender, "hisOffer": offer }))
                    await handleOffer(sender, offer)
                })
            }

        }
        else if (type == "answer") {
            // console.log('an answer to the offer came-----')

            await answerd(data)
        }
        else if (type == "candidate") {
            // console.log('candidates are received from the party ----')
            await handleCandidate(data)
        }
        else if (type == "memberAllowed") {
            if (makeKey(me, myId) != callOwner) {
                createPeer(data["sender"], "no")
                localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream))
                handleOffer(data["sender"], data["offer"])
            }
        }
        else if (type == "callOwner") {
            callOwner = data.callOwner
        }
    }


    async function sendOffer() {
        // creating offer and a local description
        peerConnection = peers[makeKey(me, myId)]
        const offer = await peerConnection.createOffer();
        peerConnection.setLocalDescription(offer)
        websoc.send(JSON.stringify({ "type": "offer", 'offer': offer, 'sender': makeKey(me, myId) }))
    }

    async function handleOffer(sender, offer) {
        // creating a peer connection, when an offer comes
        console.log("--------------------")

        peerConnection = peers[sender]
        if (peerConnection) {
            await peerConnection.setRemoteDescription(new RTCSessionDescription(offer))

            // sending the answer back accoding to offer
            const answer = await peerConnection.createAnswer()
            await peerConnection.setLocalDescription(answer)
            websoc.send(JSON.stringify({ "type": 'answer', 'answer': answer, "sender": makeKey(me, myId), "hisOffer": offer }))
        }
    }

    async function answerd(data) {
        let peerConnection = peers[data["sender"]] // 
        if (data["sender" != callOwner]) {
            // agar in bande khoda fekr mekona in answer naaq amada
            const peerConnection = createPeer(data["sender"], "no")
            localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream))
            const myGuessOffer = data["hisOffer"]
            peerConnection.setLocalDescription(myGuessOffer)
        }

        await peerConnection.setRemoteDescription(new RTCSessionDescription(data.answer));

    }

    async function handleCandidate(data) {
        if (data["sender"] != callOwner) {
            console.log("ICE came from other party, adding IceCandidate on peerConnection---", data["sender"])
            let peerConnection = peers[data["sender"]] // 
            console.log(peerConnection)
            await peerConnection.addIceCandidate(new RTCIceCandidate(data.candidate));
        }
    }

    function createPeer(user, sendAnOffer) {
        let peerConnection = new RTCPeerConnection()

        // handling any tracks to this RTC party
        peerConnection.ontrack = (event) => {
            const pair_video = document.createElement('video');
            pair_video.autoplay = true;
            pair_video.srcObject = event.streams[0];
            videosContainer.appendChild(pair_video)
        }

        //  Ice candidates comming to this RTC party 
        peerConnection.onicecandidate = (event) => {
            if (event.candidate) {
                websoc.send(JSON.stringify({ "type": "candidate", 'candidate': event.candidate, "sender": user }))
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

