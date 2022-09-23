import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { ColorSketchModule } from 'ngx-color/sketch';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { ColorPickerComponent } from './color-picker/color-picker.component';
import { WebSocketService } from './color-picker/websocket.service';

@NgModule({
  declarations: [
    AppComponent,
    ColorPickerComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    ColorSketchModule
  ],
  providers: [WebSocketService],
  bootstrap: [AppComponent]
})
export class AppModule { }
