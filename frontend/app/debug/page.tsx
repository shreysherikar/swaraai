"use client";

import { useState } from "react";

export default function DebugPage() {
  const [result, setResult] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const testAPI = async () => {
    setLoading(true);
    setResult("Testing...");

    try {
      // Log environment variables
      console.log("API_URL:", process.env.NEXT_PUBLIC_API_URL);
      console.log("API_KEY:", process.env.NEXT_PUBLIC_API_KEY ? "SET" : "NOT SET");

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "https://gyv6j2nexb.execute-api.us-east-1.amazonaws.com/prod";
      const apiKey = process.env.NEXT_PUBLIC_API_KEY || "OjUHL1nTyn9k6wX9OoxRy3Hq2oZza3AW5wpNXEBP";

      console.log("Using URL:", apiUrl);
      console.log("Using Key:", apiKey ? "SET" : "NOT SET");

      const fullUrl = `${apiUrl}/content/generate`;
      console.log("Full URL:", fullUrl);

      const response = await fetch(fullUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-api-key": apiKey,
        },
        body: JSON.stringify({
          user_id: "test_user_123",
          prompt: "Write a test message",
          content_type: "email",
        }),
      });

      console.log("Response status:", response.status);
      console.log("Response headers:", Object.fromEntries(response.headers.entries()));

      const data = await response.json();
      console.log("Response data:", data);

      setResult(JSON.stringify(data, null, 2));
    } catch (error: any) {
      console.error("Error:", error);
      setResult(`ERROR: ${error.message}\n\nStack: ${error.stack}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-8">
      <h1 className="text-3xl font-bold mb-4">API Debug Page</h1>

      <div className="mb-4 p-4 bg-gray-100 rounded">
        <h2 className="font-bold mb-2">Environment Variables:</h2>
        <p>API_URL: {process.env.NEXT_PUBLIC_API_URL || "NOT SET"}</p>
        <p>API_KEY: {process.env.NEXT_PUBLIC_API_KEY ? "SET (hidden)" : "NOT SET"}</p>
      </div>

      <button
        onClick={testAPI}
        disabled={loading}
        className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 mb-4"
      >
        {loading ? "Testing..." : "Test API"}
      </button>

      <div className="bg-white p-4 rounded border">
        <h2 className="font-bold mb-2">Result:</h2>
        <pre className="whitespace-pre-wrap text-sm">{result || "Click 'Test API' to start"}</pre>
      </div>

      <div className="mt-4 p-4 bg-yellow-50 rounded">
        <h2 className="font-bold mb-2">Instructions:</h2>
        <ol className="list-decimal list-inside space-y-2">
          <li>Click "Test API" button</li>
          <li>Open browser DevTools (F12)</li>
          <li>Check the Console tab for detailed logs</li>
          <li>Check the Network tab for the actual request</li>
        </ol>
      </div>
    </div>
  );
}
