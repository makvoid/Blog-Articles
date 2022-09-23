import { Component, OnInit } from '@angular/core'
import { catchError, tap } from 'rxjs';

import { WebSocketService } from './websocket.service';

@Component({
  selector: 'app-color-picker',
  templateUrl: './color-picker.component.html',
  styleUrls: ['./color-picker.component.css']
})
export class ColorPickerComponent implements OnInit {
  loaded = false;
  color: string = '#ffffff'
  presetColors: string[] = []

  // Watch the messages
  color$ = this.websocketService.messages$.pipe(
    catchError(error => { throw error }),
    tap({
      error: error => console.log('[WebSocket] Error:', error),
      complete: () => console.log('[WebSocket] Connection complete')
    })
  );

  constructor(public websocketService: WebSocketService) { }

  /**
   * Converts component to hex
   *
   * @param c number component to convert
   * @returns string hex of component
   */
  componentToHex (c: number) {
    var hex = c.toString(16);
    return hex.length == 1 ? "0" + hex : hex;
  }

  /**
   * Converts RGB->Hex color code
   *
   * @param r number red
   * @param g number green
   * @param b number blue
   * @returns string hex color code
   */
  rgbToHex(r: number, g: number, b: number) {
    return "#" + this.componentToHex(r) + this.componentToHex(g) + this.componentToHex(b);
  }

  /**
   * Event fired when the color change event is completed (picked)
   *
   * @param event any color change event
   */
  changeComplete(event: any) {
    this.color = event.color.hex;
    const rgb = event.color.rgb

    // Send our choice to the server
    this.websocketService.sendMessage(`${rgb.r},${rgb.g},${rgb.b}`)
  }

  /**
   * Returns a random hex color code
   *
   * @returns string hex color code
   */
  generateRandomColor () {
    return `#${Math.floor(Math.random()*16777215).toString(16)}`
  }

  ngOnInit () {
    // Generate some random colors for the presets
    this.presetColors = [...Array(24).keys()].map(() => this.generateRandomColor())

    // Listen for new messages (colors) to change to
    this.color$.subscribe((msg) => {
      // If this is our first message, we just connected
      if (!this.loaded) {
        console.log('[WebSocket] Connected')
        this.loaded = true;
      }

      // Update selected color
      const color = msg.replace('"', '').split(',').map((i: string) => parseInt(i))
      this.color = this.rgbToHex(color[0], color[1], color[2])
    })

    // Connect to the websocket
    this.websocketService.connect()
  }
}
