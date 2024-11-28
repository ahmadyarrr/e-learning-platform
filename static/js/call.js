// creating a video element and customizing it and append it to videos container
const local_video = document.getElementById('me');
local_video.autoplay = true;
const videosContainer = document.getElementById('videos')
videosContainer.appendChild(local_video)
const me = document.getElementById("username").textContent
const myId = document.getElementById("user-id").textContent

//STUN
var configuration = {
    iceServers: [
        { urls: 'stun:stun.l.google.com:19302' } // Example STUN server
    ]
};

// getting user media
var localStream;
const constranits = { 'video': true, 'audio': false }

navigator.mediaDevices.getUserMedia(constranits).then(stream => {
    localStream = stream
    let peers = {};
    let amINew = true
    let callOwner = "nobody"
    let my_channel_name;
    local_video.srcObject = stream;

    // connecting to signaling server
    const course_id = JSON.parse(document.getElementById('course-id').textContent)
    const url = "ws://" + window.location.host + "/ws/call/room/" + course_id + "/"
    const websoc = new WebSocket(url)

    websoc.onmessage = async (event) => {
        data = JSON.parse(event.data)
        message_type = data.type

        if (message_type == "user_joined") {
            if (amINew) {
                my_channel_name = data.user
                users = data.users
                users.forEach(channel_name => {
                    if (channel_name != my_channel_name) {
                        createPeerConneciton(my_channel_name, channel_name)
                    }
                });
                amINew = false
            }
        }
        else if (message_type == "offer") {
            if (data.to == my_channel_name) {
                console.log("offer came from ", data.from)
                await handleOffer(data.from, data.offer)
            }
        }
        else if (message_type == "answer") {
            if (data.to == my_channel_name) {
                console.log("answer came from..", data.from)
                await handleAnswer(data.from, data.answer)
            }

        }
        else if (message_type == "candidate") {
            console.log("--------------------------", data.candidate)
            if (data.to == my_channel_name) {
                console.log("ice candidate came... from", data.from)
                await handleIceCandidate(data.from, data.candidate)
            }
        }
        else if (message_type == "user_left") {
            console.log()
        }
    }
    async function createPeerConneciton(from, to) {
        const peerConnection = new RTCPeerConnection()
        localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream))
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
                websoc.send(JSON.stringify({ "type": "candidate", 'candidate': event.candidate, "from": my_channel_name, 'to': from }))
                sentCandidates.add(event.candidate)
            }
        };

        // creating an offer and setting local description from offer
        const offer = await peerConnection.createOffer()
        await peerConnection.setLocalDescription(offer)

        //saving the peerObject to peers
        peers[to] = peerConnection

        // sending the offer
        websoc.send(JSON.stringify({ "type": "offer", "from": from, "to": to, "offer": offer }))
        console.log("offer sent to ", to)
    }
    async function handleOffer(from, offer) {
        // this function sends an answer back to 'from' user
        const peerConnection = new RTCPeerConnection()
        localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream))
        peerConnection.ontrack = (event) => {
            const pair_video = document.createElement('video');
            pair_video.autoplay = true;
            pair_video.srcObject = event.streams[0];
            videosContainer.appendChild(pair_video)
        }
        const sentCandidates = new Set()
        //  Ice candidates comming to this RTC party 
        peerConnection.onicecandidate = (event) => {
            console.log("generating ice candidates....")
            if (event.candidate && !sentCandidates.has(event.candidate)) {
                websoc.send(JSON.stringify({ "type": "candidate", 'candidate': event.candidate, "from": my_channel_name,'to':from }))
                sentCandidates.add(event.candidate)
            }
        };
        // setting remote things
        peerConnection.setRemoteDescription(new RTCSessionDescription(offer))

        // setting the local things and sending the answer
        const answer = await peerConnection.createAnswer()
        peerConnection.setLocalDescription(answer)
        websoc.send(JSON.stringify({ "type": "answer", "answer": answer, "from": my_channel_name, "to": from }))
        console.log("answer sent to", from)
    }

    async function handleAnswer(from, answer) {
        const peerConnection = peers[from]
        await peerConnection.setRemoteDescription(new RTCSessionDescription(answer))
    }

    async function handleIceCandidate(from, candidate) {
        const peerConnection = peers[from]
        await peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
    }
})

