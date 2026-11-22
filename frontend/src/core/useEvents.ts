import { useEffect, useState, useRef } from "react";
import { API_BASE } from "./api";

export interface SystemEvent {
  id?: number;
  kind: string;
  message: string;
  detail?: any;
  created_at?: string;
}

export function useEvents(onEvent?: (event: SystemEvent) => void) {
  const [connected, setConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState<SystemEvent | null>(null);
  const callbackRef = useRef(onEvent);
  callbackRef.current = onEvent;

  useEffect(() => {
    let eventSource: EventSource | null = null;
    let reconnectTimeout: any = null;

    function connect() {
      try {
        eventSource = new EventSource(`${API_BASE}/api/events/stream`);

        eventSource.onopen = () => {
          setConnected(true);
        };

        eventSource.onmessage = (e) => {
          try {
            const data: SystemEvent = JSON.parse(e.data);
            setLastEvent(data);
            if (callbackRef.current) {
              callbackRef.current(data);
            }
          } catch {
            // Ignore parse errors on ping/keepalive messages
          }
        };

        eventSource.onerror = () => {
          setConnected(false);
          if (eventSource) {
            eventSource.close();
            eventSource = null;
          }
          // Reconnect with 3-second backoff
          reconnectTimeout = setTimeout(connect, 3000);
        };
      } catch {
        setConnected(false);
        reconnectTimeout = setTimeout(connect, 3000);
      }
    }

    connect();

    return () => {
      if (eventSource) {
        eventSource.close();
      }
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
    };
  }, []);

  return { connected, lastEvent };
}
