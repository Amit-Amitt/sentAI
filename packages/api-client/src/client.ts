export interface ApiClientConfig {
  baseUrl: string;
  fetchFn?: typeof fetch;
  headers?: HeadersInit;
}

export class ApiClient {
  private readonly baseUrl: string;
  private readonly fetchFn: typeof fetch;
  private readonly headers: HeadersInit;

  constructor(config: ApiClientConfig) {
    this.baseUrl = config.baseUrl.replace(/\/$/, "");
    this.fetchFn = config.fetchFn ?? fetch;
    this.headers = config.headers ?? {
      "Content-Type": "application/json",
    };
  }

  async get<T>(path: string, init?: RequestInit) {
    const response = await this.fetchFn(`${this.baseUrl}${path}`, {
      ...init,
      headers: {
        ...this.headers,
        ...init?.headers,
      },
      method: "GET",
    });

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}.`);
    }

    return (await response.json()) as T;
  }
}

export function createApiClient(config: ApiClientConfig) {
  return new ApiClient(config);
}
