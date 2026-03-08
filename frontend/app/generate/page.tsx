"use client";

import { useState, useEffect } from "react";
import { Sparkles, Copy, CheckCircle, Mail, Linkedin, Presentation, Loader2, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";
import { useUser } from "@/lib/userContext";
import { useRouter } from "next/navigation";

type ContentType = "email" | "linkedin" | "presentation";

export default function GeneratePage() {
  const router = useRouter();
  const { userId, isCalibrated } = useUser();
  const [prompt, setPrompt] = useState("");
  const [contentType, setContentType] = useState<ContentType>("email");
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState<string>("");
  const [authenticityScore, setAuthenticityScore] = useState<number>(0);
  const [culturalMarkers, setCulturalMarkers] = useState<string[]>([]);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string>("");

  // Check if user is calibrated
  useEffect(() => {
    if (!isCalibrated) {
      // Show warning but don't redirect immediately
      setError("Please complete voice calibration first to generate authentic content");
    }
  }, [isCalibrated]);

  const contentTypes = [
    { id: "email" as ContentType, label: "Email", icon: Mail, description: "Professional emails" },
    { id: "linkedin" as ContentType, label: "LinkedIn Post", icon: Linkedin, description: "Social media posts" },
    { id: "presentation" as ContentType, label: "Presentation", icon: Presentation, description: "Slide content" },
  ];

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError("Please enter a prompt");
      return;
    }

    if (!isCalibrated) {
      setError("Please complete voice calibration first");
      setTimeout(() => router.push("/calibrate"), 2000);
      return;
    }

    try {
      setIsGenerating(true);
      setGeneratedContent("");
      setError("");
      
      const result = await api.generateContent({
        prompt: prompt.trim(),
        contentType,
        userId,
      });

      setGeneratedContent(result.content);
      setAuthenticityScore(result.authenticityScore);
      setCulturalMarkers(result.culturalMarkersUsed);
    } catch (error: any) {
      console.error("Generation error:", error);
      const errorMsg = error.message || "Failed to generate content. Please try again.";
      setError(errorMsg);
      
      // If calibration error, redirect after showing message
      if (errorMsg.includes("calibration")) {
        setTimeout(() => router.push("/calibrate"), 3000);
      }
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(generatedContent);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error("Copy error:", error);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      handleGenerate();
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Generate Content</h1>
        <p className="text-lg text-gray-600">
          Create authentic professional content in your unique voice
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Input Section */}
        <div className="space-y-6">
          {/* Calibration Warning */}
          {!isCalibrated && (
            <div className="bg-yellow-50 border-2 border-yellow-400 rounded-xl p-6">
              <div className="flex items-start gap-3">
                <AlertCircle className="text-yellow-600 flex-shrink-0 mt-1" size={24} />
                <div>
                  <h3 className="font-semibold text-yellow-900 mb-2">Voice Calibration Required</h3>
                  <p className="text-yellow-800 text-sm mb-3">
                    Complete voice calibration to generate content with your authentic voice and cultural markers.
                  </p>
                  <button
                    onClick={() => router.push("/calibrate")}
                    className="bg-yellow-600 text-white px-4 py-2 rounded-lg hover:bg-yellow-700 font-semibold text-sm"
                  >
                    Start Calibration
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 border-2 border-red-400 rounded-xl p-4">
              <div className="flex items-start gap-3">
                <AlertCircle className="text-red-600 flex-shrink-0" size={20} />
                <p className="text-red-800 text-sm">{error}</p>
              </div>
            </div>
          )}

          <div className="bg-white rounded-xl shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">What do you want to create?</h2>
            
            {/* Content Type Selector */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Content Type
              </label>
              <div className="grid grid-cols-3 gap-3">
                {contentTypes.map((type) => {
                  const Icon = type.icon;
                  return (
                    <button
                      key={type.id}
                      onClick={() => setContentType(type.id)}
                      className={`p-4 rounded-lg border-2 transition-all ${
                        contentType === type.id
                          ? "border-primary-600 bg-primary-50"
                          : "border-gray-200 hover:border-primary-300"
                      }`}
                    >
                      <Icon
                        className={`mx-auto mb-2 ${
                          contentType === type.id ? "text-primary-600" : "text-gray-400"
                        }`}
                        size={24}
                      />
                      <div className="text-sm font-medium">{type.label}</div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Prompt Input */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Your Prompt
              </label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="E.g., 'Announce our new product launch to the team' or 'Share insights about AI in healthcare'"
                className="w-full h-32 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
              />
              <p className="text-xs text-gray-500 mt-2">
                Press Cmd/Ctrl + Enter to generate
              </p>
            </div>

            {/* Generate Button */}
            <button
              onClick={handleGenerate}
              disabled={!prompt.trim() || isGenerating}
              className="w-full bg-primary-600 text-white py-3 rounded-lg font-semibold hover:bg-primary-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles size={20} />
                  Generate Content
                </>
              )}
            </button>
          </div>

          {/* Info Card */}
          <div className="bg-gradient-to-r from-primary-50 to-accent-50 rounded-xl p-6">
            <h3 className="font-semibold mb-3 flex items-center gap-2">
              <Sparkles className="text-primary-600" size={20} />
              How It Works
            </h3>
            <ul className="space-y-2 text-sm text-gray-700">
              <li>• Your linguistic profile is injected into the AI context</li>
              <li>• Content is generated with your authentic voice patterns</li>
              <li>• Cultural markers and expressions are preserved</li>
              <li>• Professional tone is maintained throughout</li>
            </ul>
          </div>
        </div>

        {/* Output Section */}
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-md p-6 min-h-[400px]">
            {!generatedContent && !isGenerating ? (
              <div className="h-full flex flex-col items-center justify-center text-center text-gray-400">
                <Sparkles size={48} className="mb-4" />
                <p className="text-lg">Your generated content will appear here</p>
                <p className="text-sm mt-2">Enter a prompt and click generate to start</p>
              </div>
            ) : isGenerating ? (
              <div className="h-full flex flex-col items-center justify-center">
                <Loader2 className="text-primary-600 animate-spin mb-4" size={48} />
                <p className="text-lg font-medium text-gray-700">Crafting your content...</p>
                <p className="text-sm text-gray-500 mt-2">Preserving your authentic voice</p>
              </div>
            ) : (
              <>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-semibold">Generated Content</h2>
                  <button
                    onClick={handleCopy}
                    className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors text-sm font-medium"
                  >
                    {copied ? (
                      <>
                        <CheckCircle size={16} className="text-green-600" />
                        Copied!
                      </>
                    ) : (
                      <>
                        <Copy size={16} />
                        Copy
                      </>
                    )}
                  </button>
                </div>

                <div className="prose max-w-none">
                  <pre className="whitespace-pre-wrap font-sans text-sm text-gray-700 bg-gray-50 p-4 rounded-lg">
                    {generatedContent}
                  </pre>
                </div>
              </>
            )}
          </div>

          {/* Authenticity Metrics */}
          {generatedContent && (
            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="font-semibold mb-4">Authenticity Metrics</h3>
              
              {/* Authenticity Score */}
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Authenticity Score</span>
                  <span className="text-sm font-bold text-primary-600">
                    {Math.round(authenticityScore * 100)}%
                  </span>
                </div>
                <div className="bg-gray-200 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-primary-600 to-accent-600 h-full transition-all duration-500"
                    style={{ width: `${authenticityScore * 100}%` }}
                  />
                </div>
              </div>

              {/* Cultural Markers */}
              <div>
                <span className="text-sm font-medium text-gray-700 block mb-2">
                  Cultural Markers Used
                </span>
                <div className="flex flex-wrap gap-2">
                  {culturalMarkers.map((marker, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-xs font-medium"
                    >
                      {marker}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Example Prompts */}
      <div className="mt-12 bg-white rounded-xl shadow-md p-8">
        <h2 className="text-2xl font-bold mb-6">Example Prompts to Try</h2>
        <div className="grid md:grid-cols-3 gap-6">
          <div>
            <h3 className="font-semibold mb-2 flex items-center gap-2">
              <Mail size={18} className="text-primary-600" />
              Email Examples
            </h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>• "Follow up on project deadline"</li>
              <li>• "Request feedback on proposal"</li>
              <li>• "Announce team meeting"</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold mb-2 flex items-center gap-2">
              <Linkedin size={18} className="text-primary-600" />
              LinkedIn Examples
            </h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>• "Share career milestone"</li>
              <li>• "Discuss industry trends"</li>
              <li>• "Celebrate team achievement"</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold mb-2 flex items-center gap-2">
              <Presentation size={18} className="text-primary-600" />
              Presentation Examples
            </h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>• "Quarterly results overview"</li>
              <li>• "Product roadmap update"</li>
              <li>• "Team strategy session"</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
