// creating a video element and customizing it and append it to videos container
const local_video = document.getElementById('me');
local_video.autoplay = true;
const videosContainer = document.getElementById('videos')
videosContainer.appendChild(local_video)

// getting user media
var localStream;
const constranits = { 'video': true, 'audio': true }
navigator.mediaDevices.getUserMedia(constranits).then(stream => {
    localStream = stream
    let myUserName;
    let peers = new Array();
    let peerConnection = new RTCPeerConnection();
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
            websoc.send(JSON.stringify({ "type": "candidate", 'candidate': event.candidate }))
        }
    };
    
    localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream))
    local_video.srcObject = stream;

    // making the url of call consumer
    const course_id = JSON.parse(document.getElementById('course-id').textContent)
    const url = "ws://" + window.location.host + "/ws/call/room/" + course_id + "/"
    const websoc = new WebSocket(url)
    var peerCounter = 0

    // receving the answer and handling it with appropriate method
    websoc.onmessage = async (event) => {
        const data = JSON.parse(event.data)
        const type = data.type
        const user = data.user
        if (type == 'joined') {
            peers.push(peerConnection); 
            peerCounter += 1 
            console.log("user joied ", peers.length,peerConnection)
            if (peerCounter > 1) {
                console.log("lenght > 1")
                document.getElementById("peers").innerHTML += `<button type="button" id="call${user}" >call${user}</button>`
                document.getElementById(`call${user}`).addEventListener("click", function(){
                    sendOffer(myUserName);
                } )
            }
            else{
                myUserName = user;
            }
        }
        else if (type == 'left') {
            console.log('user left---')
        }
        else if (type == 'offer') {
            if (data.sender != myUserName){
                console.log("handling the offer ")
                await handleOffer(data)

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
    }


    async function sendOffer(senderName) {
        // creating offer and a local description
        const offer = await peerConnection.createOffer();
        peerConnection.setLocalDescription(offer)
        websoc.send(JSON.stringify({ "type": "offer", 'offer': offer, 'sender':senderName}))
    }

    async function handleOffer(data) {
        // creating a peer connection, when an offer comes
        await peerConnection.setRemoteDescription(new RTCSessionDescription(data.offer))

        // sending the answer back accoding to offer
        const answer = await peerConnection.createAnswer()
        await peerConnection.setLocalDescription(answer)
        websoc.send(JSON.stringify({ "type":'answer','answer': answer}))
    }

    async function answerd(data) {
        console.log(' other party answered, setting remote description---')
        const peerConnection = peers[0]
        await peerConnection.setRemoteDescription(new RTCSessionDescription(data.answer));

    }

    async function handleCandidate(data) {
        console.log("ICE came from other party, adding IceCandidate on peerConnection---")
        const peerConnection = peers[0];
        await peerConnection.addIceCandidate(new RTCIceCandidate(data.candidate));

    }



}).catch(error => {
    console.log('error in acheving access to media', error)
})

