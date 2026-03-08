"use client";

import { useUser } from "@/lib/userContext";
import { useRouter } from "next/navigation";

export default function TestCalibrationPage() {
  const router = useRouter();
  const { isCalibrated, setCalibrated, resetCalibration } = useUser();

  return (
    <div className="max-w-2xl mx-auto p-8">
      <h1 className="text-2xl font-bold mb-4">Calibration Test Page</h1>
      
      <div className="bg-white p-6 rounded-lg shadow mb-4">
        <p className="mb-4">
          Current Status: <strong>{isCalibrated ? "Calibrated ✅" : "Not Calibrated ❌"}</strong>
        </p>
        
        <div className="space-x-4">
          <button
            onClick={() => setCalibrated(true)}
            className="bg-green-600 text-white px-6 py-3 rounded-lg"
          >
            Mark as Calibrated
          </button>
          
          <button
            onClick={() => resetCalibration()}
            className="bg-red-600 text-white px-6 py-3 rounded-lg"
          >
            Reset Calibration
          </button>
          
          <button
            onClick={() => router.push("/generate")}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg"
          >
            Go to Generate
          </button>
        </div>
      </div>
      
      <div className="bg-yellow-50 p-4 rounded-lg">
        <p className="text-sm">
          <strong>Note:</strong> This is a test page. Use "Mark as Calibrated" to simulate completing voice calibration without actually recording.
        </p>
      </div>
    </div>
  );
}
