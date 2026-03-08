import Link from "next/link";
import { Mic, FileText, User, Sparkles } from "lucide-react";

export default function Home() {
  return (
    <div className="max-w-6xl mx-auto">
      {/* Hero Section */}
      <div className="text-center py-16">
        <h1 className="text-5xl font-bold text-gray-900 mb-4">
          Welcome to <span className="text-primary-600">Swara</span>
        </h1>
        <p className="text-xl text-gray-600 mb-2">
          Your AI Identity Layer for Linguistic Sovereignty
        </p>
        <p className="text-lg text-gray-500 mb-8">
          Preserve your authentic voice in professional communications
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/calibrate"
            className="bg-primary-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-primary-700 transition-colors"
          >
            Get Started
          </Link>
          <Link
            href="/generate"
            className="bg-white text-primary-600 px-8 py-3 rounded-lg font-semibold border-2 border-primary-600 hover:bg-primary-50 transition-colors"
          >
            Generate Content
          </Link>
        </div>
      </div>

      {/* Features Grid */}
      <div className="grid md:grid-cols-3 gap-8 py-12">
        <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow">
          <div className="bg-primary-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
            <Mic className="text-primary-600" size={24} />
          </div>
          <h3 className="text-xl font-semibold mb-2">Voice Calibration</h3>
          <p className="text-gray-600 mb-4">
            Upload voice samples to create your unique linguistic profile
          </p>
          <Link href="/calibrate" className="text-primary-600 font-medium hover:underline">
            Calibrate Now →
          </Link>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow">
          <div className="bg-accent-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
            <FileText className="text-accent-600" size={24} />
          </div>
          <h3 className="text-xl font-semibold mb-2">Content Generation</h3>
          <p className="text-gray-600 mb-4">
            Generate emails, posts, and presentations in your authentic voice
          </p>
          <Link href="/generate" className="text-accent-600 font-medium hover:underline">
            Generate Content →
          </Link>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow">
          <div className="bg-primary-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
            <User className="text-primary-600" size={24} />
          </div>
          <h3 className="text-xl font-semibold mb-2">Your Profile</h3>
          <p className="text-gray-600 mb-4">
            View your linguistic DNA and cultural markers
          </p>
          <Link href="/profile" className="text-primary-600 font-medium hover:underline">
            View Profile →
          </Link>
        </div>
      </div>

      {/* Impact Stats */}
      <div className="bg-gradient-to-r from-primary-600 to-accent-600 text-white rounded-2xl p-12 my-12">
        <div className="flex items-center justify-center mb-6">
          <Sparkles size={32} />
        </div>
        <h2 className="text-3xl font-bold text-center mb-8">
          Eliminate the Code-Switching Tax
        </h2>
        <div className="grid md:grid-cols-3 gap-8 text-center">
          <div>
            <div className="text-4xl font-bold mb-2">40%</div>
            <div className="text-white/90">Faster Content Drafting</div>
          </div>
          <div>
            <div className="text-4xl font-bold mb-2">25%</div>
            <div className="text-white/90">Higher Engagement</div>
          </div>
          <div>
            <div className="text-4xl font-bold mb-2">50M+</div>
            <div className="text-white/90">Indian Professionals</div>
          </div>
        </div>
      </div>

      {/* How It Works */}
      <div className="py-12">
        <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="bg-primary-600 text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">
              1
            </div>
            <h3 className="text-xl font-semibold mb-2">Upload Voice</h3>
            <p className="text-gray-600">
              Share audio samples to capture your unique linguistic patterns
            </p>
          </div>
          <div className="text-center">
            <div className="bg-primary-600 text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">
              2
            </div>
            <h3 className="text-xl font-semibold mb-2">AI Analysis</h3>
            <p className="text-gray-600">
              Our AI extracts your prosody, cadence, and cultural expressions
            </p>
          </div>
          <div className="text-center">
            <div className="bg-primary-600 text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">
              3
            </div>
            <h3 className="text-xl font-semibold mb-2">Generate Content</h3>
            <p className="text-gray-600">
              Create authentic professional content that sounds like you
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
