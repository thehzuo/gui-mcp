import "@testing-library/jest-dom/vitest";

class MockEventSource {
  url: string;
  onmessage: ((event: MessageEvent) => void) | null = null;

  constructor(url: string) {
    this.url = url;
  }

  addEventListener() {}
  close() {}
}

Object.defineProperty(window, "EventSource", {
  writable: true,
  value: MockEventSource
});

