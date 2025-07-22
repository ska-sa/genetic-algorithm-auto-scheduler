import { Routes } from '@angular/router';
import { UserComponent } from './components/user/user.component';
import { TimetablesComponent } from './components/timetables/timetables.component';
import { TimetableDetailsComponent } from './components/timetable-details/timetable-details.component';

export const routes: Routes = [
    {
        path: '', redirectTo: 'user/timetables', pathMatch: 'full'
    },
    {
        path: 'user', component: UserComponent, children: [
            {
                path: 'timetables', component: TimetablesComponent, children: [
                    {
                        path: ':id/details', component: TimetableDetailsComponent
                    },
                ]
            }
        ]
    }
];
