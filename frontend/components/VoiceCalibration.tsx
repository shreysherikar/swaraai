"use client";

import { useState, useRef, useEffect } from "react";
import { useUser } from "@/lib/userContext";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

interface CalibrationQuestion {
  id: number;
  question: string;
  category: string;
}

const CALIBRATION_QUESTIONS: CalibrationQuestion[] = [
  { id: 1, question: "Tell me about yourself and what you do professionally.", category: "Introduction" },
  { id: 2, question: "Describe a typical day at your work or studies.", category: "Daily Life" },
  { id: 3, question: "What are your thoughts on technology and innovation in India?", category: "Opinion" },
  { id: 4, question: "Share a memorable experience from your childhood or recent past.", category: "Storytelling" },
  { id: 5, question: "How do you usually communicate with your friends and family?", category: "Communication Style" },
];

export default function VoiceCalibration() {
  const router = useRouter();
  const { setCalibrated, setUserId } = useUser();
  const [mode, setMode] = useState<"choice" | "live" | "upload">("choice");
  const [isRecording, setIsRecording] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [recordedChunks, setRecordedChunks] = useState<Blob[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [calibrationComplete, setCalibrationComplete] = useState(false);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    return () => {
      stopRecording();
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const startLiveCalibration = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      setMode("live");
      setCurrentQuestion(0);
    } catch (error) {
      alert("Microphone access denied. Please allow microphone access to continue.");
    }
  };

  const startRecording = () => {
    if (!streamRef.current) return;

    try {
      // Try different MIME types for better browser compatibility
      let options: MediaRecorderOptions = { mimeType: 'audio/webm' };
      
      if (!MediaRecorder.isTypeSupported('audio/webm')) {
        if (MediaRecorder.isTypeSupported('audio/mp4')) {
          options = { mimeType: 'audio/mp4' };
        } else if (MediaRecorder.isTypeSupported('audio/ogg')) {
          options = { mimeType: 'audio/ogg' };
        } else if (MediaRecorder.isTypeSupported('audio/wav')) {
          options = { mimeType: 'audio/wav' };
        } else {
          options = {}; // Use default
        }
      }

      const mediaRecorder = new MediaRecorder(streamRef.current, options);
      mediaRecorderRef.current = mediaRecorder;

      const chunks: Blob[] = [];
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        setRecordedChunks(prev => [...prev, ...chunks]);
      };

      mediaRecorder.start();
      setIsRecording(true);

      // Auto-stop after 30 seconds per question
      timerRef.current = setTimeout(() => {
        stopRecording();
        moveToNextQuestion();
      }, 30000);
    } catch (error) {
      console.error("MediaRecorder error:", error);
      alert("Recording failed. Your browser may not support audio recording. Please try uploading a file instead or use Chrome/Edge.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    }
  };

  const moveToNextQuestion = () => {
    if (currentQuestion < CALIBRATION_QUESTIONS.length - 1) {
      setCurrentQuestion(prev => prev + 1);
    } else {
      finishCalibration();
    }
  };

  const skipQuestion = () => {
    stopRecording();
    moveToNextQuestion();
  };

  const finishCalibration = async () => {
    stopRecording();
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }

    // Check if we have any recorded audio
    if (recordedChunks.length === 0) {
      alert("No audio recorded. Please record at least one answer before finishing.");
      return;
    }

    setIsProcessing(true);

    try {
      // Combine all recorded chunks with proper MIME type
      const mimeType = recordedChunks.length > 0 && recordedChunks[0].type 
        ? recordedChunks[0].type 
        : 'audio/webm';
      
      const combinedBlob = new Blob(recordedChunks, { type: mimeType });
      
      console.log("Combined audio blob:", combinedBlob.size, "bytes, type:", mimeType);
      
      // Process the audio (send to backend)
      await processAudio(combinedBlob);
      
      // Clear recorded chunks for security
      setRecordedChunks([]);
      
      setIsProcessing(false);
      setCalibrationComplete(true);
    } catch (error) {
      console.error("Calibration error:", error);
      setIsProcessing(false);
      alert(`Calibration failed: ${error instanceof Error ? error.message : 'Unknown error'}. Please try again or use file upload.`);
    }
  };

  const processAudio = async (audioBlob: Blob) => {
    try {
      // Call the API with the audio file
      const result = await api.uploadVoice(new File([audioBlob], "calibration.webm", { type: audioBlob.type }));
      
      console.log("Voice upload result:", result);
      
      const jobId = result.job_id;
      
      // Store job_id as user_id
      setUserId(jobId);
      
      // Poll for completion
      let attempts = 0;
      const maxAttempts = 60; // 5 minutes max (5 second intervals)
      
      while (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 5000)); // Wait 5 seconds
        
        try {
          const status = await api.checkVoiceStatus(jobId);
          console.log("Status check:", status);
          
          if (status.profile_ready) {
            // Profile is ready!
            console.log("Profile ready:", status);
            setCalibrated(true);
            return;
          }
          
          if (status.status === 'FAILED') {
            throw new Error("Voice processing failed");
          }
          
          // Still processing, continue polling
          attempts++;
        } catch (error) {
          console.error("Status check error:", error);
          attempts++;
        }
      }
      
      // Timeout
      throw new Error("Voice processing timed out. Please try again.");
      
    } catch (error) {
      console.error("Failed to process audio:", error);
      alert("Failed to process audio. Please try again.");
      throw error;
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith("audio/")) {
      alert("Please upload an audio file");
      return;
    }

    // Validate file size (max 50MB)
    if (file.size > 50 * 1024 * 1024) {
      alert("File size must be less than 50MB");
      return;
    }

    setIsProcessing(true);
    await processAudio(file);
    setIsProcessing(false);
    setCalibrationComplete(true);
  };

  if (calibrationComplete) {
    return (
      <div className="max-w-2xl mx-auto text-center py-12">
        <div className="bg-green-50 border-2 border-green-500 rounded-lg p-8">
          <div className="text-6xl mb-4">✅</div>
          <h2 className="text-2xl font-bold text-green-800 mb-2">
            Calibration Complete!
          </h2>
          <p className="text-green-700 mb-6">
            Your linguistic identity has been captured. Your voice data was processed and immediately deleted for security.
          </p>
          <p className="text-green-700 mb-6 font-semibold">
            You can now generate unlimited content without talking again!
          </p>
          <button
            onClick={() => router.push("/generate")}
            className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700"
          >
            Start Generating Content
          </button>
        </div>
      </div>
    );
  }

  if (mode === "choice") {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">Voice Calibration</h1>
          <p className="text-gray-600 text-lg">
            Choose how you'd like to calibrate your linguistic identity
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Live Recording Option */}
          <div className="border-2 border-blue-500 rounded-lg p-8 hover:shadow-lg transition-shadow">
            <div className="text-5xl mb-4">🎤</div>
            <h3 className="text-2xl font-bold mb-3">Live Recording</h3>
            <p className="text-gray-600 mb-4">
              Answer guided questions while we capture your natural speaking style
            </p>
            <ul className="text-sm text-gray-500 mb-6 space-y-2">
              <li>✓ 5 guided questions</li>
              <li>✓ ~2 minutes total</li>
              <li>✓ Most accurate results</li>
              <li>✓ No data stored</li>
            </ul>
            <button
              onClick={startLiveCalibration}
              className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 font-semibold"
            >
              Start Live Recording
            </button>
          </div>

          {/* File Upload Option */}
          <div className="border-2 border-gray-300 rounded-lg p-8 hover:shadow-lg transition-shadow">
            <div className="text-5xl mb-4">📁</div>
            <h3 className="text-2xl font-bold mb-3">Upload Audio File</h3>
            <p className="text-gray-600 mb-4">
              Already have a recording? Upload it here
            </p>
            <ul className="text-sm text-gray-500 mb-6 space-y-2">
              <li>✓ MP3, WAV, M4A supported</li>
              <li>✓ Max 50MB file size</li>
              <li>✓ 2+ minutes recommended</li>
              <li>✓ Deleted after processing</li>
            </ul>
            <label className="block w-full bg-gray-600 text-white py-3 rounded-lg hover:bg-gray-700 font-semibold text-center cursor-pointer">
              Choose Audio File
              <input
                type="file"
                accept="audio/*"
                onChange={handleFileUpload}
                className="hidden"
              />
            </label>
          </div>
        </div>

        <div className="mt-8 p-4 bg-blue-50 rounded-lg">
          <p className="text-sm text-blue-800">
            <strong>Privacy Note:</strong> Your voice data is processed in real-time and immediately deleted. 
            We only store linguistic patterns (speech rate, cultural markers) - never the actual audio.
          </p>
        </div>
      </div>
    );
  }

  if (mode === "live") {
    const progress = ((currentQuestion + 1) / CALIBRATION_QUESTIONS.length) * 100;
    const question = CALIBRATION_QUESTIONS[currentQuestion];

    return (
      <div className="max-w-3xl mx-auto">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Question {currentQuestion + 1} of {CALIBRATION_QUESTIONS.length}</span>
            <span>{Math.round(progress)}% Complete</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-blue-600 h-3 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Question Card */}
        <div className="bg-white border-2 border-gray-200 rounded-lg p-8 mb-6">
          <div className="text-sm text-blue-600 font-semibold mb-2">
            {question.category}
          </div>
          <h2 className="text-2xl font-bold mb-6">
            {question.question}
          </h2>

          {/* Recording Indicator */}
          {isRecording && (
            <div className="flex items-center justify-center mb-6">
              <div className="animate-pulse flex items-center space-x-3">
                <div className="w-4 h-4 bg-red-500 rounded-full"></div>
                <span className="text-red-500 font-semibold">Recording...</span>
              </div>
            </div>
          )}

          {/* Controls */}
          <div className="flex gap-4 justify-center">
            {!isRecording ? (
              <button
                onClick={startRecording}
                className="bg-blue-600 text-white px-8 py-4 rounded-lg hover:bg-blue-700 font-semibold text-lg"
              >
                🎤 Start Speaking
              </button>
            ) : (
              <button
                onClick={() => {
                  stopRecording();
                  moveToNextQuestion();
                }}
                className="bg-green-600 text-white px-8 py-4 rounded-lg hover:bg-green-700 font-semibold text-lg"
              >
                ✓ Next Question
              </button>
            )}
            
            <button
              onClick={skipQuestion}
              className="bg-gray-300 text-gray-700 px-6 py-4 rounded-lg hover:bg-gray-400 font-semibold"
            >
              Skip
            </button>
          </div>
        </div>

        {/* Tips */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-sm text-yellow-800">
            <strong>💡 Tip:</strong> Speak naturally as you would with friends or colleagues. 
            Use your everyday expressions and don't worry about being formal.
          </p>
        </div>

        {/* Finish Early Option */}
        {currentQuestion >= 2 && (
          <div className="mt-4 text-center">
            <button
              onClick={finishCalibration}
              className="text-blue-600 hover:underline text-sm"
            >
              I've spoken enough - Finish calibration
            </button>
          </div>
        )}
      </div>
    );
  }

  if (isProcessing) {
    return (
      <div className="max-w-2xl mx-auto text-center py-12">
        <div className="animate-spin text-6xl mb-4">⚙️</div>
        <h2 className="text-2xl font-bold mb-2">Processing Your Voice...</h2>
        <p className="text-gray-600 mb-4">
          Analyzing linguistic patterns and cultural markers
        </p>
        <p className="text-sm text-gray-500">
          This takes 1-2 minutes. Please wait...
        </p>
      </div>
    );
  }

  return null;
}
