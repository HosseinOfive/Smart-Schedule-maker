"use client";

import React, { useState } from 'react';
import { View, Views } from 'react-big-calendar';
import UploadWidget from './components/dashboard/UploadWidget';
import CalendarPanel from './components/dashboard/CalendarPanel';


// This matches the JSON  Python Backend sends back
interface MasterScheduleItem {
  title: string;
  start: string; // ISO String from backend
  end: string;
  location: string;
  type: 'fixed' | 'suggested';
  validation_status: 'Valid' | 'Impossible' | 'Unknown';
  validation_message?: string;
}

export default function Home() {
  // states
  const [events, setEvents] = useState<any[]>([]); 
  const [view, setView] = useState<View>(Views.WEEK); 
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState<string>("");

  // handler
  const handleFileProcess = async (file: File) => {
    setUploadStatus('uploading');
    setErrorMessage("");
    console.log("📤 Sending file to backend:", file.name);

    //Prepare the File for transport
    const formData = new FormData();
    formData.append('file', file); 

    try {
      //Send to Python Backend (port should be 8000)
      const response = await fetch('http://127.0.0.1:8000/upload_ics', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server Error: ${response.statusText}`);
      }

      //wait for response of json data
      const data = await response.json();
      console.log("📥 Received from backend:", data);

    
      const parsedEvents = data.map((evt: MasterScheduleItem) => ({
        ...evt,
        start: new Date(evt.start),
        end: new Date(evt.end),
      }));

      // Update UI
      setEvents(parsedEvents);
      setUploadStatus('success');

    } catch (error: any) {
      console.error("❌ Upload Failed:", error);
      setErrorMessage("Could not connect to Backend. Is FastAPI running?");
      setUploadStatus('error');
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 flex flex-col items-center py-10 px-4">
      
      {/* 1. Header Section */}
      <div className="w-full max-w-5xl mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 tracking-tight">Smart-Schedule-maker</h1>
          <p className="text-gray-500 mt-1">AI-Powered Student Scheduler</p>
        </div>
        
        {/* Status Badge */}
        {uploadStatus === 'success' && (
          <span className="px-4 py-1 bg-green-100 text-green-700 text-sm font-medium rounded-full border border-green-200">
            Schedule Optimized
          </span>
        )}
        {uploadStatus === 'error' && (
          <span className="px-4 py-1 bg-red-100 text-red-700 text-sm font-medium rounded-full border border-red-200">
            Connection Error
          </span>
        )}
      </div>

      {/* 2. Upload Area */}
      <div className="w-full max-w-5xl mb-8 bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
         <h2 className="text-sm font-semibold text-gray-500 mb-4 uppercase tracking-wider">1. Upload Timetable</h2>
         <UploadWidget onFileSelect={handleFileProcess} status={uploadStatus} />
         
         {/* Error Message Display */}
         {errorMessage && (
           <div className="mt-4 p-3 bg-red-50 text-red-600 text-sm rounded-lg border border-red-100">
             ⚠️ {errorMessage}
           </div>
         )}
      </div>

      {/* 3. Calendar Area */}
      <div className="w-full max-w-5xl flex-1 bg-white p-6 rounded-2xl shadow-xl border border-gray-200 min-h-[600px] flex flex-col">
        <h2 className="text-sm font-semibold text-gray-500 mb-4 uppercase tracking-wider">2. Your Optimized Schedule</h2>
        
        <div className="flex-1">
          <CalendarPanel 
            events={events} 
            view={view} 
            onViewChange={setView} 
          />
        </div>
      </div>

    </main>
  );
}