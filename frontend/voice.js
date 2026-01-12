// Voice interaction module for Construction Agent

class VoiceManager {
    constructor() {
        this.isRecording = false;
        this.isPlaying = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.audioQueue = [];
        this.voiceEnabled = false;
        this.currentAudio = null;
    }

    // Initialize voice capabilities
    async init() {
        // Check if browser supports required APIs
        if (!navigator.mediaDevices || !window.MediaRecorder) {
            console.warn('Voice features not supported in this browser');
            return false;
        }

        try {
            // Request microphone permission
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            stream.getTracks().forEach(track => track.stop()); // Stop immediately, just checking permission
            return true;
        } catch (error) {
            console.error('Microphone permission denied:', error);
            return false;
        }
    }

    // Start recording audio
    async startRecording() {
        if (this.isRecording) return;

        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    channelCount: 1,
                    sampleRate: 16000,
                    sampleSize: 16
                }
            });

            this.mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus'
            });

            this.audioChunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };

            this.mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                stream.getTracks().forEach(track => track.stop());
                await this.processRecording(audioBlob);
            };

            this.mediaRecorder.start();
            this.isRecording = true;

            // Update UI
            this.updateRecordingUI(true);

            console.log('🎤 Recording started');
        } catch (error) {
            console.error('Error starting recording:', error);
            alert('Could not access microphone. Please check permissions.');
        }
    }

    // Stop recording
    stopRecording() {
        if (!this.isRecording || !this.mediaRecorder) return;

        this.mediaRecorder.stop();
        this.isRecording = false;
        this.updateRecordingUI(false);

        console.log('🛑 Recording stopped');
    }

    // Process recorded audio
    async processRecording(audioBlob) {
        try {
            // Show processing state
            this.showProcessingState('Transcribing...');

            // Create FormData for upload
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');

            // Send to backend for transcription
            const response = await fetch(`${API_BASE}/transcribe`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Transcription failed');
            }

            const data = await response.json();
            const transcribedText = data.text;

            console.log('📝 Transcribed:', transcribedText);

            // Add transcribed text to input
            const messageInput = document.getElementById('message-input');
            messageInput.value = transcribedText;

            // Automatically send the message if voice is enabled
            if (this.voiceEnabled) {
                await this.sendMessageWithVoice(transcribedText);
            }

            this.hideProcessingState();

        } catch (error) {
            console.error('Error processing recording:', error);
            alert('Failed to transcribe audio. Please try again.');
            this.hideProcessingState();
        }
    }

    // Send message and handle voice response
    async sendMessageWithVoice(text) {
        // This will be called by the main app
        // After getting response, call speakText()
    }

    // Convert text to speech and play
    async speakText(text, voiceId = null) {
        if (!this.voiceEnabled) return;

        try {
            // Clean text for speech (remove markdown, code blocks, etc.)
            const cleanText = this.cleanTextForSpeech(text);

            // Stop any current audio
            this.stopCurrentAudio();

            // Show speaking indicator
            this.updateSpeakingUI(true);

            // Request TTS from backend
            const response = await fetch(`${API_BASE}/text-to-speech`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: cleanText,
                    voice_id: voiceId
                })
            });

            if (!response.ok) {
                throw new Error('TTS failed');
            }

            // Get audio data
            const audioBlob = await response.blob();
            const audioUrl = URL.createObjectURL(audioBlob);

            // Create audio element and play
            this.currentAudio = new Audio(audioUrl);

            this.currentAudio.onended = () => {
                this.updateSpeakingUI(false);
                URL.revokeObjectURL(audioUrl);
                this.currentAudio = null;
            };

            this.currentAudio.onerror = (error) => {
                console.error('Audio playback error:', error);
                this.updateSpeakingUI(false);
            };

            await this.currentAudio.play();

        } catch (error) {
            console.error('Error in text-to-speech:', error);
            this.updateSpeakingUI(false);

            // Fall back to browser TTS
            this.fallbackToWebSpeech(text);
        }
    }

    // Fallback to browser's speech synthesis
    fallbackToWebSpeech(text) {
        if ('speechSynthesis' in window) {
            const cleanText = this.cleanTextForSpeech(text);
            const utterance = new SpeechSynthesisUtterance(cleanText);
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            utterance.volume = 0.8;

            // Use a better voice if available
            const voices = window.speechSynthesis.getVoices();
            const preferredVoice = voices.find(v =>
                v.name.includes('Google') ||
                v.name.includes('Microsoft') ||
                v.name.includes('Samantha') // macOS
            );

            if (preferredVoice) {
                utterance.voice = preferredVoice;
            }

            utterance.onend = () => {
                this.updateSpeakingUI(false);
            };

            this.updateSpeakingUI(true);
            window.speechSynthesis.speak(utterance);
        }
    }

    // Clean text for speech (remove markdown, etc.)
    cleanTextForSpeech(text) {
        return text
            .replace(/```[\s\S]*?```/g, '') // Remove code blocks
            .replace(/`[^`]+`/g, '') // Remove inline code
            .replace(/[*_~]/g, '') // Remove markdown emphasis
            .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Convert links to text
            .replace(/^#+\s/gm, '') // Remove headers
            .replace(/^-\s/gm, '') // Remove list markers
            .substring(0, 500); // Limit length for voice
    }

    // Stop current audio playback
    stopCurrentAudio() {
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.currentAudio = null;
        }
        if (window.speechSynthesis) {
            window.speechSynthesis.cancel();
        }
        this.updateSpeakingUI(false);
    }

    // Toggle voice mode
    toggleVoice() {
        this.voiceEnabled = !this.voiceEnabled;

        const voiceToggle = document.getElementById('voice-toggle');
        const voiceInputBtn = document.getElementById('voice-input-btn');

        if (this.voiceEnabled) {
            voiceToggle.textContent = '🔊 Voice On';
            voiceToggle.classList.add('active');
            voiceInputBtn.style.display = 'block';
        } else {
            voiceToggle.textContent = '🎙️ Voice Off';
            voiceToggle.classList.remove('active');
            voiceInputBtn.style.display = 'none';
            this.stopCurrentAudio();
        }

        return this.voiceEnabled;
    }

    // UI Update functions
    updateRecordingUI(isRecording) {
        const voiceInputBtn = document.getElementById('voice-input-btn');
        const messageInput = document.getElementById('message-input');
        const sendBtn = document.getElementById('send-btn');

        if (isRecording) {
            voiceInputBtn.classList.add('recording');
            voiceInputBtn.innerHTML = '🔴';
            messageInput.disabled = true;
            messageInput.placeholder = 'Listening...';
            sendBtn.disabled = true;
        } else {
            voiceInputBtn.classList.remove('recording');
            voiceInputBtn.innerHTML = '🎤';
            messageInput.disabled = false;
            messageInput.placeholder = 'Ask about ceiling heights, clearances, specifications...';
            sendBtn.disabled = false;
        }
    }

    updateSpeakingUI(isSpeaking) {
        const indicator = document.getElementById('speaking-indicator');
        if (!indicator) {
            // Create speaking indicator if it doesn't exist
            const div = document.createElement('div');
            div.id = 'speaking-indicator';
            div.className = 'speaking-indicator hidden';
            div.innerHTML = '🔊 Speaking...';
            document.getElementById('input-container').appendChild(div);
        }

        const speakingIndicator = document.getElementById('speaking-indicator');
        if (isSpeaking) {
            speakingIndicator.classList.remove('hidden');
        } else {
            speakingIndicator.classList.add('hidden');
        }
    }

    showProcessingState(message) {
        const thinkingIndicator = document.getElementById('thinking-indicator');
        thinkingIndicator.innerHTML = `<span class="dots">...</span> ${message}`;
        thinkingIndicator.classList.remove('hidden');
    }

    hideProcessingState() {
        const thinkingIndicator = document.getElementById('thinking-indicator');
        thinkingIndicator.classList.add('hidden');
    }
}

// Export for use in main app
window.VoiceManager = VoiceManager;