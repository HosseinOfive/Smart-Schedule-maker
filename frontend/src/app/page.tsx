"use client";

import React, { useState } from 'react';
import { View, Views } from 'react-big-calendar';
import UploadWidget from './components/dashboard/UploadWidget';
import CalendarPanel from './components/dashboard/CalendarPanel';

// --- Types & Mock Data ---

interface MasterScheduleItem {
  title: string;
  start: string; 
  end: string;
  location: string;
  type: 'fixed' | 'suggested';
  validation_status: 'Valid' | 'Impossible' | 'Unknown';
  validation_message?: string;
}

const MOCK_API_RESPONSE: MasterScheduleItem[] = [
  {
    title: "CSCB07: Software Design",
    start: "2026-01-05T09:00:00",
    end: "2026-01-05T11:00:00",
    location: "UTSC SW319",
    type: "fixed",
    validation_status: "Valid"
  },
  {
    title: "Gym: Leg Day",
    start: "2026-01-05T11:15:00",
    end: "2026-01-05T12:30:00",
    location: "Pan Am Sports Centre",
    type: "suggested",
    validation_status: "Impossible",
    validation_message: "Travel time (20m) exceeds gap (15m)"
  },
  {
    title: "CSCB36: Theory of Computation",
    start: "2026-01-07T14:00:00",
    end: "2026-01-07T16:00:00",
    location: "UTSC IC130",
    type: "fixed",
    validation_status: "Valid"
  }
];

export default function Home() {
  // --- STATE ---
  const [events, setEvents] = useState<any[]>([]); 
  const [view, setView] = useState<View>(Views.WEEK); 
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success'>('idle');

  // --- HANDLERS ---
  const handleFileProcess = (file: File) => {
    setUploadStatus('uploading');
    console.log("Processing:", file.name);

    // Mock API Call
    setTimeout(() => {
      const parsedEvents = MOCK_API_RESPONSE.map(evt => ({
        ...evt,
        start: new Date(evt.start),
        end: new Date(evt.end),
      }));
      setEvents(parsedEvents);
      setUploadStatus('success');
    }, 1500);
  };

  return (
    <main className="min-h-screen bg-gray-50 flex flex-col items-center py-10 px-4">
      
      {/* 1. Header Section */}
      <div className="w-full max-w-5xl mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 tracking-tight">ChronoCommute</h1>
          <p className="text-gray-500 mt-1">AI-Powered Student Scheduler</p>
        </div>
        
        {/* Simple Status Badge */}
        {uploadStatus === 'success' && (
          <span className="px-4 py-1 bg-green-100 text-green-700 text-sm font-medium rounded-full border border-green-200">
            Schedule Optimized
          </span>
        )}
      </div>

      {/* 2. Upload Area */}
      <div className="w-full max-w-5xl mb-8 bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
         <h2 className="text-sm font-semibold text-gray-500 mb-4 uppercase tracking-wider">1. Upload Timetable</h2>
         <UploadWidget onFileSelect={handleFileProcess} status={uploadStatus} />
      </div>

      {/* 3. Calendar Area (Now Full Width) */}
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