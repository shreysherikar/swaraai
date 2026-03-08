"use client";

import { useState } from "react";

export default function TestAPIPage() {
  const [result, setResult] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const testAPI = async () => {
    setLoading(true);
    setResult("");
    
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL;
      const API_KEY = process.env.NEXT_PUBLIC_API_KEY;
      
      setResult(`Testing API...\nURL: ${API_URL}\nKey: ${API_KEY?.substring(0, 10)}...`);
      
      const response = await fetch(`${API_URL}/content/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-api-key": API_KEY || "",
        },
        body: JSON.stringify({
          user_id: "test_user_123",
          prompt: "Write a short test message",
          content_type: "general",
        }),
      });
      
      const data = await response.json();
      setResult(JSON.stringify(data, null, 2));
    } catch (error: any) {
      setResult(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-8">
      <h1 className="text-2xl font-bold mb-4">API Test Page</h1>
      <button
        onClick={testAPI}
        disabled={loading}
        className="bg-blue-600 text-white px-6 py-3 rounded-lg mb-4"
      >
        {loading ? "Testing..." : "Test API"}
      </button>
      <pre className="bg-gray-100 p-4 rounded-lg overflow-auto max-h-96">
        {result || "Click button to test API"}
      </pre>
    </div>
  );
}
