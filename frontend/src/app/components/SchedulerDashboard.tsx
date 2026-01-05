"use client";

import React, { useState } from 'react';
import { View, Views } from 'react-big-calendar';
import UploadWidget from './dashboard/UploadWidget';
import CalendarPanel from './dashboard/CalendarPanel';
///import MapPanel from './dashboard/MapPanel'; 

export default function SchedulerDashboard() {
  // states
  const [events, setEvents] = useState<any[]>([]); // Replace any with proper type
  const [view, setView] = useState<View>(Views.WEEK);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success'>('idle');

  
  const handleFileProcess = (file: File) => {
    setUploadStatus('uploading');
    console.log("Processing:", file.name);
   
    setTimeout(() => {

        setUploadStatus('success');
    }, 1000);
  };

  return (
    <div className="flex h-screen w-full bg-gray-100 overflow-hidden">
      
      {/* LEFT PANEL */}
      <div className="w-5/12 flex flex-col h-full border-r border-gray-200 bg-white shadow-xl z-10">
        <div className="p-6 border-b border-gray-100">
          <h1 className="text-2xl font-bold text-gray-800 mb-4">ChronoCommute</h1>
          
          {/* COMPONENT 1: Upload */}
          <UploadWidget onFileSelect={handleFileProcess} status={uploadStatus} />
        </div>

        <div className="flex-1 p-4 overflow-hidden">
          {/* COMPONENT 2: Calendar */}
          <CalendarPanel events={events} view={view} onViewChange={setView} />
        </div>
      </div>

      {/* RIGHT PANEL */}
      <div className="flex-1 relative bg-slate-200">
         {/* COMPONENT 3: Map */}
         {/* <MapPanel ... /> */}
         <div className="p-10 text-center text-gray-500">Map Component Here</div>
      </div>

    </div>
  );
}