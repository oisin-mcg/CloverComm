// JavaScript for WebRTC

let localStream;
let peerConnection;
const configuration = {
    iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] // Google's public STUN server
};
let encryptionKey;

// Call elements from the HTML
const callButton = document.getElementById('start-call');
const hangupButton = document.getElementById('hangup');
const callIDInput = document.getElementById('call_id');
const passwordInput = document.getElementById('password');
const localAudio = document.getElementById('localAudio');
const remoteAudio = document.getElementById('remoteAudio');

//function to fetch and display user count if the app were to be deployed on a web server (this will always be 0 on a local testing envioroment due to an issue with windows port rules)
/*async function fetchConnectionCount() {
    try {
        const response = await fetch('/get_connection_count');
        const data = await response.json();
        alert(`Current active connections: ${data.connection_count}`);
    } catch (error) {
        console.error('Error fetching connection count:', error);
    }
}*/

//function to generate encryption key from password for client-side
//i derive a salt key from the call ID and password 
async function generateKey(callID, password) {
    const encoder = new TextEncoder();
    const keyMaterial = await window.crypto.subtle.importKey(
        'raw',
        encoder.encode(password),
        'PBKDF2',
        false,
        ['deriveKey']
    );
    //derive key
    return window.crypto.subtle.deriveKey(
        {
            name: 'PBKDF2',
            salt: encoder.encode(callID),
            iterations: 100000,
            hash: 'SHA-256'
        },
        keyMaterial,
        { name: 'AES-GCM', length: 256 },
        true,
        ['encrypt', 'decrypt']
    );
}

//encrypt our audio data before sending
// i use the generated key
async function encryptData(data) {
    const iv = window.crypto.getRandomValues(new Uint8Array(12));
    const encrypted = await window.crypto.subtle.encrypt(
        {
            name: 'AES-GCM',
            iv: iv
        },
        encryptionKey,
        data
    );
    return { iv, encrypted };
}

//this function handles data decryption
async function decryptData(encryptedData, iv) {
    try {
        const decrypted = await window.crypto.subtle.decrypt(
            {
                name: 'AES-GCM',
                iv: iv
            },
            encryptionKey,
            encryptedData
        );
        return decrypted;
    } catch (e) {
        console.error('Decryption failed:', e);
        return null;
    }
}

//event listener for the star call btn 
callButton.addEventListener('click', async () => {
    const callID = callIDInput.value;
    const password = passwordInput.value;

    if (!callID || !password) {
        alert('Please enter both Call ID and Password.');
        return;
    }

    //wait for encryption function to complete to avoid connecting prematurly
    encryptionKey = await generateKey(callID, password);

        //ask user for microphone permission to stream mic data then start sending data 
    try {
        localStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        localAudio.srcObject = localStream;
    } catch (err) {
        console.error('Error accessing media devices.', err);
        return;
    }

    //begin peer to peer connection
    peerConnection = new RTCPeerConnection(configuration);
    localStream.getTracks().forEach(track => {
        peerConnection.addTrack(track, localStream);
    });



    /*these two functions would be used in the event of deployment, 
    *it sets up the client side for ICE deplyment however due to the time and hardware constraints i am unable to set up a local ICE server
    *this is just an example of how i would implement it 
    *to test you count install pip flask socket however you would need to modify app.py to operate at its start as a ICE server which was
    *casuing confiling issues and traceback errors with my group memeber scode
    */
    ///notify user of connection
    peerConnection.ontrack = event => {
        const [remoteStream] = event.streams;
        remoteAudio.srcObject = remoteStream;
        notifyUser("A participant has connected to the call!");
    };

    peerConnection.onicecandidate = event => {
        if (event.candidate) {
            // Handle ICE candidate exchange with a signaling server
        }
    };

    try {
        const offer = await peerConnection.createOffer();
        await peerConnection.setLocalDescription(offer);
        // Send the offer to the remote peer
    } catch (err) {
        console.error('Error creating or sending offer:', err);
    }

    fetchConnectionCount();
});

//hang up the call
if (hangupButton) {
    hangupButton.addEventListener('click', () => {
        if (peerConnection) {
            peerConnection.close();
            peerConnection = null;
        }
        if (localStream) {
            localStream.getTracks().forEach(track => track.stop());
            localStream = null;
        }
        localAudio.srcObject = null;
        remoteAudio.srcObject = null;
        alert('Call ended successfully.');
    });
}

//onload function
window.onload = () => {
    // i would use this funcition in a real world application to alert users that their connection must be https to fucntion
  //  if (location.protocol !== 'https:') {
   //     alert('WebRTC and secure features require HTTPS.');
  //  }
    fetchConnectionCount();
    if (Notification.permission !== "granted") {
        Notification.requestPermission();
    }
};
