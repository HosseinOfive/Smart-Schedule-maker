"use client";
import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

interface UploadWidgetProps {
  onFileSelect: (file: File) => void;
  status: 'idle' | 'uploading' | 'success';
}

export default function UploadWidget({ onFileSelect, status }: UploadWidgetProps) {
  
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onFileSelect(acceptedFiles[0]);
    }
  }, [onFileSelect]);

     /////I am casting with any deal with it later!
  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop,
    maxFiles: 1,
    accept: {
      'text/calendar': ['.ics']
    }
  } as any); 

  return (
    <div 
      {...getRootProps()} 
      className={`p-6 border-2 border-dashed rounded-xl transition-all cursor-pointer text-center select-none
        ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400 bg-gray-50'}`}
    >
      {}
      <input {...(getInputProps() as any)} />
      
      {status === 'uploading' ? (
        <div className="flex flex-col items-center gap-2">
          <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-blue-600 font-medium">Parsing Timetable...</p>
        </div>
      ) : status === 'success' ? (
        <p className="text-green-600 font-bold">✅ Success! Schedule Loaded.</p>
      ) : (
        <div>
          <p className="text-gray-600 font-medium text-sm lg:text-base">Drop your .ics file here</p>
          <p className="text-xs text-gray-400 mt-1 uppercase tracking-wider">UofT / Outlook / Apple</p>
        </div>
      )}
    </div>
  );
}