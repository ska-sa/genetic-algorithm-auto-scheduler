import { Routes } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { GenerateComponent } from './generate/generate.component';

export const routes: Routes = [
    {
        path: "", component: HomeComponent
    },
    {
        path: "generate", component: GenerateComponent
    }
];
