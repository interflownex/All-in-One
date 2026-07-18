import { EventEmitter, Uri, type Event } from "vscode";

export interface IDataViewerDataProvider {
  readonly id: string;
  getRows(): Promise<Array<Record<string, unknown>>>;
}

export type Resource = Uri;

export interface IExtensionApi {
  ready: Promise<void>;
  debug: {
    getRemoteLauncherCommand(
      host: string,
      port: number,
      waitUntilDebuggerAttaches: boolean,
    ): Promise<string[]>;
    getDebuggerPackagePath(): Promise<string | undefined>;
  };
  settings: {
    readonly onDidChangeExecutionDetails: Event<Uri | undefined>;
    getExecutionDetails(resource?: Resource): {
      execCommand: string[] | undefined;
    };
  };
  datascience: {
    showDataViewer(dataProvider: IDataViewerDataProvider, title: string): Promise<void>;
  };
}

export function createExtensionApi(): IExtensionApi {
  const executionDetailsEmitter = new EventEmitter<Uri | undefined>();

  return {
    async ready() {
      return;
    },

    debug: {
      async getRemoteLauncherCommand(
        host: string,
        port: number,
        waitUntilDebuggerAttaches: boolean,
      ) {
        return [
          "python",
          "-m",
          "debugpy",
          "--listen",
          `${host}:${port}`,
          ...(waitUntilDebuggerAttaches ? ["--wait-for-client"] : []),
        ];
      },

      async getDebuggerPackagePath() {
        return "/usr/local/lib/python3.x/site-packages/debugpy";
      },
    },

    settings: {
      onDidChangeExecutionDetails: executionDetailsEmitter.event,

      getExecutionDetails(resource?: Resource) {
        const command = resource ? ["/usr/bin/python3", "-u"] : ["/usr/bin/python3", "-u"];

        return {
          execCommand: command,
        };
      },
    },

    datascience: {
      async showDataViewer(dataProvider: IDataViewerDataProvider, title: string) {
        console.log(`Opening data viewer: ${title} for ${dataProvider.id}`);
      },
    },
  };
}

export function emitExecutionDetailsChange(resource: Uri | undefined): void {
  const emitter = new EventEmitter<Uri | undefined>();
  emitter.fire(resource);
}
