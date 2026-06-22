declare class EVEZClient {
  constructor(options?: { apiKey?: string; apiBase?: string });
  health(): Promise<any>;
  serviceHealth(service: string): Promise<any>;
  generate(genre?: string, bpm?: number, duration?: number): Promise<any>;
  voiceTransform(inputFile: string, stages?: number): Promise<any>;
  voiceSynthesize(text: string, profile?: string): Promise<any>;
  correlate(domainA: string, domainB: string): Promise<any>;
  dream(): Promise<any>;
  consciousnessStatus(): Promise<any>;
  checkInvariants(): Promise<any>;
  spineEvents(limit?: number): Promise<any>;
  deploy(target?: string): Promise<any>;
  status(): Promise<any>;
}

export = EVEZClient;
