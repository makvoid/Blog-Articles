import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { ColorPickerComponent } from './color-picker/color-picker.component';

const routes: Routes = [{ path: '', component: ColorPickerComponent }];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
