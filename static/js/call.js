// creating a video element and customizing it and append it to videos container
const local_video = document.createElement('video');
local_video.autoplay = true;
local_video.muted = true;
document.getElementById('videos').appendChild(local_video)

// getting user media
var localStream;
const constranits = {'video': true, 'audio':true} 
navigator.mediaDevices.getUserMedia(constranits).then(stream => {
    local_video.srcObject = stream;
    localStream  = stream
    local_video.muted = true;
}).catch(error =>{
    console.log('error in acheving access to media',error)
})

// making the url of call consumer
const course_id  = JSON.parse(document.getElementById('course-id').textContent)
const username = JSON.parse(document.getElementById('username').textContent)
const url = "ws://"+window.location.host+"/ws/call/room/"+course_id+"/"
const websoc = new WebSocket(url)


let peers = {};
// receving the answer and handling it with appropriate method
websoc.onmessage = async (event)=>{
    const data = JSON.parse(event.data)
    const type = data.type
    const user = data.user
    if (type=='user_joined'){
        console.log('user joined---',user);
        await createPeerConnection(user);
    }
    else if (type=='user_left'){
        console.log('user left----')
    
    }
    else if (type == 'offer'){
        console.log('an offer is comming from a party---')
        await handleOffer(data)
    }
    else if (type == "answer"){
        console.log('an answer to the offer came-----')
        await answerd(data)
    }
    else if (type == "candidate"){
        console.log('candidates are received from the party ----')
        await handleCandidate(data)
    }
}

// sending the offer
console.log(websoc,'-----------------offer websocket----------------')
websoc.send(peers)


async function createPeerConnection(data){
    console.log('createing peer connection with the new user ----')
    const peerConnection = new RTCPeerConnection();
    peers[data.user] = peerConnection;
    console.log(localStream,'----localstram-----in--crete')
    localStream.getTracks().forEach(track => peerConnection.addTrack(track,localStream))
    console.log('Getting tracks-------')

    // handling any tracks
    peerConnection.ontrack = (event)=>{
        const pair_video = document.createElement('video');
        pair_video.autoplay =true;
        pair_video.srcObject = event.streams[0];
        document.getElementById('videos').appendChild(pair_video)
    }

    //  candidate paths 
    peerConnection.onicecandidate = (event) => {
        if (event.candidate){
            websoc.send(JSON.stringify({'candidate':event.candidate,'user':user}))
        }
    };
    
    // creating offer and a local description
    const offer = await peerConnection.createOffer();
    peerConnection.setLocalDescription(offer)
    websoc.send(JSON.stringify({'offer':offer,'user':user}))
    console.log('offer send from JS-----')
    return peerConnection
    }



async function handleOffer(data){
    console.log('handle offer JS called ----')
    // creating a peer connection, when an offer comes
    const peerConnection = createPeerConnection(data.user);
    await peerConnection.setRemoteDescription(new RTCSessionDescription(data.offer))
    
    // sending the answer back accoding to offer
    const answer = await peerConnection.createAnswer()
    await peerConnection.setLocalDescription(answer)
    websoc.send(JSON.stringify({'answer':answer,'user':data.user}))
}

async function answerd(data){
    console.log('handlAnswer JS called ---')
    const peerConnection  = peers[data.user]
    await peerConnection.setRemoteDescription(new RTCSessionDescription(data.answer));

}

async function handleCandidate(data){
    console('candidate JS called----')
    const peerConnection = peers[data.user];
    await peerConnection.addIceCandidate(new RTCIceCandidate(data.candidate));

}