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

// Function to fetch and display the connection count from the Flask app
async function fetchConnectionCount() {
    try {
        const response = await fetch('/get_connection_count');
        const data = await response.json();
        alert(`Current active connections: ${data.connection_count}`);
    } catch (error) {
        console.error('Error fetching connection count:', error);
    }
}

// Generate encryption key from password for client-side
async function generateKey(callID, password) {
    const encoder = new TextEncoder();
    const keyMaterial = await window.crypto.subtle.importKey(
        'raw',
        encoder.encode(password),
        'PBKDF2',
        false,
        ['deriveKey']
    );
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

// Encrypt audio data before sending
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

// Decrypt audio data received from connection
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

// Start call
callButton.addEventListener('click', async () => {
    const callID = callIDInput.value;
    const password = passwordInput.value;

    if (!callID || !password) {
        alert('Please enter both Call ID and Password.');
        return;
    }

    encryptionKey = await generateKey(callID, password);

    try {
        localStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        localAudio.srcObject = localStream;
    } catch (err) {
        console.error('Error accessing media devices.', err);
        return;
    }

    peerConnection = new RTCPeerConnection(configuration);
    localStream.getTracks().forEach(track => {
        peerConnection.addTrack(track, localStream);
    });

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

// Hang up the call
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

// Onload function
window.onload = () => {
    if (location.protocol !== 'https:') {
        alert('WebRTC and secure features require HTTPS.');
    }
    fetchConnectionCount();
    if (Notification.permission !== "granted") {
        Notification.requestPermission();
    }
};
