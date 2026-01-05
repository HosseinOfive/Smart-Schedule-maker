"use client";
import React from 'react';
import { Calendar, dateFnsLocalizer, View, Views } from 'react-big-calendar';


import { format, parse, startOfWeek, getDay } from 'date-fns';
import { enUS } from 'date-fns/locale';

import 'react-big-calendar/lib/css/react-big-calendar.css';


const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek,
  getDay,
  locales: {
    'en-US': enUS,
  },
});

//  interfaces
interface CalendarEvent {
  title: string;
  start: Date;
  end: Date;
  location: string;
  type: 'fixed' | 'suggested';
  validation_status: 'Valid' | 'Impossible' | 'Unknown';
}

interface CalendarPanelProps {
  events: CalendarEvent[];
  view: View; 
  onViewChange: (v: View) => void;
}

export default function CalendarPanel({ events, view, onViewChange }: CalendarPanelProps) {
  
  
  const eventStyleGetter = (event: CalendarEvent) => {
    let backgroundColor = '#3b82f6'; // Default Blue
    if (event.type === 'suggested') backgroundColor = '#10b981'; // Green
    if (event.validation_status === 'Impossible') backgroundColor = '#ef4444'; // Red
    
    return { 
      style: { 
        backgroundColor, 
        borderRadius: '6px', 
        opacity: 0.9, 
        color: 'white',
        border: '0px',
        display: 'block'
      } 
    };
  };

  return (
    <div className="h-full bg-white p-2 rounded-lg text-slate-700">
      <Calendar
        localizer={localizer}
        events={events}
        startAccessor="start"
        endAccessor="end"
        view={view}
        onView={onViewChange}
        style={{ height: '100%' }}
        eventPropGetter={eventStyleGetter}
        // This ensures the calendar works well with the date-fns v4 locale object
        culture='en-US'
      />
    </div>
  );
}