<template>
    <div class="container">
        <div class="controller">
            <div class="select-block">
                <div class="event-options">
                    <label for="event"></label>
                    <select v-model="form.eventName" name="event" required>
                        <option value="Session 1">Session 1</option>
                        <option value="Session 2">Session 2</option>
                        <option value="Session 3">Session 3</option>
                        <option value="Session 4">Session 4</option>
                    </select>
                </div>
                <div class="type-options">
                    <label for="type"></label>
                    <select v-model="form.typeName" name="type" required>
                        <option value="Check in">Check in</option>
                        <option value="Check out">Check out</option>
                    </select>
                </div>
            </div>
            <div class="control-block">
                <p>Camera status: <span :class="{active: isScanning}">{{ isScanning ? 'Active' : 'Inactive' }}</span></p>
                <button @click="startScanner">Start</button>
            </div>
        </div>
        
        <div v-if="isScanning" class="qr-scanner">
            <video ref="video" autoplay></video>
            <canvas ref="canvas" style="display: none;"></canvas>
        </div>
        <div v-if=" form.QRcode!=='' && !isScanning " class="review-information">
            <h1>Review Information</h1>
            <p>Event name: {{ form.eventName }}</p>
            <p>Type: {{ form.typeName }}</p>
            <p>Code: {{ form.QRcode }}</p>
        </div>
        
    </div>
</template>
  
<script>
import jsQR from 'jsqr';
import axios from 'axios';

export default {
    data() {
        return {
            video: null,
            canvas: null,
            canvasContext: null,
            requestAnimationId: null,
            isScanning: false,
            form: {
                eventName: "Session 1",
                typeName: "Check in",
                QRcode: "",
            }
        };
    },
    methods: {
        sendDataToServer(){
            const serverAddress = 'http://127.0.0.1:5000/sendData'
            axios.post(serverAddress,this.form)
            .then(response => {
                console.log('Server Response:', response.data);
            })
            .catch(error => {
                console.error('Error:', error);
            })
        },
        startScanner() {
            this.isScanning = true;
            this.form.QRcode = ""
            this.$nextTick(() => { // Ensures the DOM updates with the video and canvas elements
                this.video = this.$refs.video;
                this.canvas = this.$refs.canvas;
                if (this.canvas && this.video) {
                    this.canvasContext = this.canvas.getContext('2d');
                    this.setupCamera();
                } else {
                    console.error('Video or Canvas elements are not available.');
                }
            });
        },
        setupCamera() {
            navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
                .then(stream => {
                    this.video.srcObject = stream;
                    this.requestAnimationId = requestAnimationFrame(this.tick);
                })
                .catch(error => {
                    console.error('Error accessing the camera:', error);
                    this.isScanning = false; // Stop scanning if there's an error
                });
        },
        tick() {
            if (this.video.readyState === this.video.HAVE_ENOUGH_DATA) {
                this.canvas.height = this.video.videoHeight;
                this.canvas.width = this.video.videoWidth;
                this.canvasContext.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
                const imageData = this.canvasContext.getImageData(0, 0, this.canvas.width, this.canvas.height);
                const code = jsQR(imageData.data, imageData.width, imageData.height, {
                    inversionAttempts: "dontInvert",
                });

                if (code) {
                    console.log('Detected QR Code:', code.data);
                    this.form.QRcode = code.data
                    if (code.data!==""){
                        cancelAnimationFrame(this.requestAnimationId); // Optionally stop scanning after the first QR code is detected
                        this.isScanning = false; // Update UI to reflect scanning has stopped
                        this.sendDataToServer() // send data to server
                    }
                    else {
                        console.log('QRcode is not right. Please scan again!');
                        this.requestAnimationId = requestAnimationFrame(this.tick);
                    }
                } else {
                    this.requestAnimationId = requestAnimationFrame(this.tick);
                }
            } else {
                this.requestAnimationId = requestAnimationFrame(this.tick);
            }
        }
    },

    beforeUnmount() {
        if (this.requestAnimationId) {
            cancelAnimationFrame(this.requestAnimationId);
        }
        if (this.video && this.video.srcObject) {
            this.video.srcObject.getTracks().forEach(track => track.stop());
        }
    }
};
</script>

<style scoped>
    .container{
        padding-top: 5%;
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        font-family: Arial, Helvetica, sans-serif;
        gap: 20px
    }
    .container .controller{
        padding: 20px;
        border-radius: 8px;
        width: 20%;
        background-color: antiquewhite;
    }
    .controller .select-block{
        width: 100%;
        display: flex;
        justify-content: space-around;
        font-size: 25px;
    }
    .select-block select{
        width: 100px;
        height: 40px;
        font-size: 15px;
        border-radius: 10px;
    }
    .controller .control-block{
        width: 100%;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 25px;
    }
    .control-block button{
        width: 100px;
        height: 50px;
        font-size: 18px;
        border-radius: 10px;
    }
    .control-block p span{
        color: red;
    }
    .control-block p .active{
        color: green;
    }
    .container .qr-scanner video{
        border-radius: 15px;
    }
    .container .review-information{
        font-size: 20px;
    }
</style>