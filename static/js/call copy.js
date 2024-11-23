// creating a video element and customizing it and append it to videos container
const local_video = document.createElement('video');
local_video.autoplay = true;
document.getElementById('videos').appendChild(local_video)

// getting user media
var localStream;
const constranits = { 'video': true, 'audio': true }
navigator.mediaDevices.getUserMedia(constranits).then(stream => {
    local_video.srcObject = stream;
    localStream = stream
    // making the url of call consumer
    const course_id = JSON.parse(document.getElementById('course-id').textContent)
    const url = "ws://" + window.location.host + "/ws/call/room/" + course_id + "/"
    const websoc = new WebSocket(url)
    var counter  = 0

    let peers = {};
    // receving the answer and handling it with appropriate method
    websoc.onmessage = async (event) => {
        const data = JSON.parse(event.data)
        const type = data.type
        const user = data.user
        if (type == 'joined') {
            counter += 1
            console.log('user joined---', counter);
            await createPeerConnection(user);
        }
        else if (type == 'left') {
            counter +=1
            console.log('user left---',counter)
        }
        else if (type == 'offer') {
            await handleOffer(data)
        }
        else if (type == "answer") {
            // console.log('an answer to the offer came-----')
            await answerd(data)
        }
        else if (type == "candidate") {
            // console.log('candidates are received from the party ----')
            await handleCandidate(data)
        }
    }


    async function createPeerConnection(user) {
        let peerConnection = new RTCPeerConnection();
        localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream))
        peers[user] = peerConnection;

        // handling any tracks
        peerConnection.ontrack = (event) => {
            counter += 1
            console.log("track comming from other side---",counter)
            const pair_video = document.createElement('video');
            pair_video.autoplay = true;
            pair_video.srcObject = event.streams[0];
            document.getElementById('videos').appendChild(pair_video)
        }

        //  candidate paths 
        peerConnection.onicecandidate = (event) => {
            counter += 1
            console.log("ice candidate came from new user---",counter )
            if (event.candidate) {
                websoc.send(JSON.stringify({ "type":"candidate",'candidate': event.candidate, 'user': user }))
            }
        };

        // creating offer and a local description
        const offer = await peerConnection.createOffer();
        peerConnection.setLocalDescription(offer)
        websoc.send(JSON.stringify({ "type":"offer",'offer': offer, 'user': user }))
        counter +=1
        console.log('offer send on to new user---',counter)
        return peerConnection
    }

    async function handleOffer(data) {
        // creating a peer connection, when an offer comes
        counter +=1
        console.log("offer came from other party---", counter)
        const peerConnection = createPeerConnection(data.user);
        await peerConnection.setRemoteDescription(new RTCSessionDescription(data.offer))

        // sending the answer back accoding to offer
        const answer = await peerConnection.createAnswer()
        await peerConnection.setLocalDescription(answer)
        websoc.send(JSON.stringify({ 'answer': answer, 'user': data.user }))
        counter +=1
        console.log("answer sent back to other party---", counter)
    }

    async function answerd(data) {
        counter += 1
        console.log(' other party answered, setting remote description---', counter)
        const peerConnection = peers[data.user]
        await peerConnection.setRemoteDescription(new RTCSessionDescription(data.answer));

    }

    async function handleCandidate(data) {
        counter +=1
        console.log("ICE came from other party, adding IceCandidate on peerConnection---", counter)
        const peerConnection = peers[data.user];
        await peerConnection.addIceCandidate(new RTCIceCandidate(data.candidate));

    }



}).catch(error => {
    console.log('error in acheving access to media', error)
})

