import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { HlmToasterImports } from '@spartan-ng/helm/sonner';

@Component({
  imports: [RouterOutlet, HlmToasterImports],
  selector: 'app-root',
  styleUrl: './app.css',
  templateUrl: './app.html',
})
export class App {
  protected readonly title = signal('frontend');
}
