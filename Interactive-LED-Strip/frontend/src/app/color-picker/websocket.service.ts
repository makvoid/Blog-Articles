import { Injectable } from '@angular/core';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { catchError, tap, switchAll, retryWhen, delayWhen } from 'rxjs/operators';
import { EMPTY, Observable, Subject, timer } from 'rxjs';

import { environment } from '../../environments/environment';

export const WS_ENDPOINT = environment.endpoint
export const RECONNECT_INTERVAL = 5000

@Injectable({
  providedIn: 'root'
})
export class WebSocketService {
  public socket$: WebSocketSubject<any>;
  private messagesSubject$ = new Subject();
  public messages$ = this.messagesSubject$.pipe(switchAll(), catchError(e => { throw e }));

  connect (cfg: { reconnect: boolean } = { reconnect: false }): void {
    console.log('[WebSocket] Connecting to host')
    if (!this.socket$ || this.socket$.closed) {
      this.socket$ = this.getNewWebSocket();
      const messages = this.socket$.pipe(cfg.reconnect ? this.reconnect : o => o,
        tap({
          error: error => console.log(error),
        }), catchError(_ => EMPTY))
      this.messagesSubject$.next(messages);
    }
  }

  getNewWebSocket() {
    return webSocket({
      url: WS_ENDPOINT,
      closeObserver: {
        next: () => {
          console.log('[WebSocket] Connection closed');
          this.socket$ = undefined;
          this.connect({ reconnect: true });
        }
      },
    });
  }

  reconnect (observable: Observable<any>): Observable<any> {
    return observable.pipe(
      retryWhen(errors => errors.pipe(tap(() => console.log('[WebSocket] Trying to reconnect')),
      delayWhen(_ => timer(RECONNECT_INTERVAL)))));
  }

  sendMessage (msg: any) {
    this.socket$.next(msg);
  }

  close () {
    this.socket$.complete();
  }
}