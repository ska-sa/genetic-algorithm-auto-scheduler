import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';


export const timetableGuard: CanActivateFn = (route, state) => {
  
  if (route.url.toString().includes("/0/")) {
    return false;
  } else { // if id == 0, then bloock access
    //inject(Router).navigate(['user', 'timetables']);
    return true;
  }
};
