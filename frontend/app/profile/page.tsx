"use client";

import { useState, useEffect } from "react";
import { User, Mic, TrendingUp, RefreshCw, Loader2, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";
import type { LinguisticProfile } from "@/lib/mockApi";
import Link from "next/link";
import { useUser } from "@/lib/userContext";
import { useRouter } from "next/navigation";

export default function ProfilePage() {
  const router = useRouter();
  const { isCalibrated, resetCalibration } = useUser();
  const [profile, setProfile] = useState<LinguisticProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadProfile();
  }, [isCalibrated]);

  const loadProfile = async () => {
    try {
      setIsLoading(true);
      
      // If not calibrated, show calibration prompt
      if (!isCalibrated) {
        setProfile(null);
        setIsLoading(false);
        return;
      }
      
      const data = await api.getUserProfile();
      setProfile(data);
    } catch (error) {
      console.error("Failed to load profile:", error);
      setProfile(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRecalibrate = () => {
    if (confirm("Are you sure you want to recalibrate? This will update your linguistic profile.")) {
      resetCalibration();
      router.push("/calibrate");
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="flex flex-col items-center justify-center py-20">
          <Loader2 className="text-primary-600 animate-spin mb-4" size={48} />
          <p className="text-lg text-gray-600">Loading your profile...</p>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-xl shadow-md p-12 text-center">
          <div className="bg-gray-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
            <AlertCircle className="text-gray-400" size={40} />
          </div>
          <h2 className="text-2xl font-bold mb-4">No Profile Found</h2>
          <p className="text-gray-600 mb-8">
            You haven't calibrated your voice yet. Upload voice samples to create your linguistic profile.
          </p>
          <Link
            href="/calibrate"
            className="inline-block bg-primary-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-primary-700 transition-colors"
          >
            Start Calibration
          </Link>
        </div>
      </div>
    );
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Your Linguistic Profile</h1>
        <p className="text-lg text-gray-600">
          Your unique voice signature and cultural markers
        </p>
      </div>

      {/* Profile Header */}
      <div className="bg-gradient-to-r from-primary-600 to-accent-600 text-white rounded-xl shadow-md p-8 mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="bg-white/20 p-4 rounded-full">
              <User size={32} />
            </div>
            <div>
              <h2 className="text-2xl font-bold">User Profile</h2>
              <p className="text-white/90">ID: {profile.userId}</p>
            </div>
          </div>
          <button
            onClick={handleRecalibrate}
            className="bg-white text-primary-600 px-6 py-3 rounded-lg font-semibold hover:bg-white/90 transition-colors flex items-center gap-2"
          >
            <RefreshCw size={20} />
            Re-calibrate
          </button>
        </div>
      </div>

      {/* Confidence Score */}
      <div className="bg-white rounded-xl shadow-md p-8 mb-8">
        <div className="flex items-center gap-3 mb-6">
          <TrendingUp className="text-primary-600" size={24} />
          <h3 className="text-xl font-semibold">Profile Confidence</h3>
        </div>
        
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-700 font-medium">Overall Confidence Score</span>
            <span className="text-2xl font-bold text-primary-600">
              {Math.round(profile.confidence * 100)}%
            </span>
          </div>
          <div className="bg-gray-200 rounded-full h-4 overflow-hidden">
            <div
              className="bg-gradient-to-r from-primary-600 to-accent-600 h-full transition-all duration-500"
              style={{ width: `${profile.confidence * 100}%` }}
            />
          </div>
        </div>

        <p className="text-sm text-gray-600">
          Last calibrated: {formatDate(profile.lastCalibrated)}
        </p>
      </div>

      {/* Prosody Features */}
      <div className="bg-white rounded-xl shadow-md p-8 mb-8">
        <div className="flex items-center gap-3 mb-6">
          <Mic className="text-primary-600" size={24} />
          <h3 className="text-xl font-semibold">Prosody Features</h3>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="text-sm text-gray-600 mb-1">Speech Rate</div>
            <div className="text-2xl font-bold text-gray-900">
              {profile.prosodyFeatures.speechRate} <span className="text-sm font-normal">wpm</span>
            </div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="text-sm text-gray-600 mb-1">Pause Patterns</div>
            <div className="text-lg font-semibold text-gray-900">
              {profile.prosodyFeatures.pausePatterns}
            </div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="text-sm text-gray-600 mb-1">Tonal Variation</div>
            <div className="text-lg font-semibold text-gray-900">
              {profile.prosodyFeatures.tonalVariation}
            </div>
          </div>
        </div>
      </div>

      {/* Cultural Markers */}
      <div className="bg-white rounded-xl shadow-md p-8 mb-8">
        <h3 className="text-xl font-semibold mb-4">Cultural Markers</h3>
        <p className="text-gray-600 mb-4">
          Unique linguistic patterns identified in your voice
        </p>
        <div className="flex flex-wrap gap-3">
          {profile.culturalMarkers.map((marker, index) => (
            <div
              key={index}
              className="px-4 py-2 bg-primary-100 text-primary-700 rounded-lg font-medium"
            >
              {marker}
            </div>
          ))}
        </div>
      </div>

      {/* Hinglish Patterns */}
      <div className="bg-white rounded-xl shadow-md p-8">
        <h3 className="text-xl font-semibold mb-4">Hinglish Patterns</h3>
        <p className="text-gray-600 mb-4">
          Common expressions and code-mixing patterns
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {profile.hinglishPatterns.map((pattern, index) => (
            <div
              key={index}
              className="px-4 py-2 bg-accent-100 text-accent-700 rounded-lg font-medium text-center"
            >
              "{pattern}"
            </div>
          ))}
        </div>
      </div>

      {/* Info Section */}
      <div className="mt-8 bg-gradient-to-r from-primary-50 to-accent-50 rounded-xl p-6">
        <h3 className="font-semibold mb-3">About Your Profile</h3>
        <ul className="space-y-2 text-sm text-gray-700">
          <li>• Your linguistic profile is unique to you and captures your authentic voice</li>
          <li>• Cultural markers help preserve your Indian English expressions</li>
          <li>• Prosody features ensure generated content matches your speaking style</li>
          <li>• Re-calibrate anytime to update your profile with new voice samples</li>
          <li>• All data is encrypted and stored securely</li>
        </ul>
      </div>
    </div>
  );
}
