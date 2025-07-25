import { Routes } from '@angular/router';
import { UserComponent } from './components/user/user.component';
import { TimetablesComponent } from './components/timetables/timetables.component';
import { TimetableDetailsComponent } from './components/timetable-details/timetable-details.component';
//import { EditTimetableComponent } from './components/edit-timetable/edit-timetable.component';
import { GenerateTimetableComponent } from './components/generate-timetable/generate-timetable.component';
import { timetableGuard } from './guards/timetable.guard';

export const routes: Routes = [
    {
        path: '', redirectTo: 'user/timetables', pathMatch: 'full'
    },
    {
        path: 'user', component: UserComponent, children: [
            {
                path: 'timetables', component: TimetablesComponent
            },
            {
                path: 'timetables/:id/details', component: TimetableDetailsComponent, canActivate: [timetableGuard]
            },/*
            {
                path: 'timetables/:id/edit', component: EditTimetableComponent
            },*/
            {
                path: 'timetables/generate', component: GenerateTimetableComponent
            },
        ]
    }
];