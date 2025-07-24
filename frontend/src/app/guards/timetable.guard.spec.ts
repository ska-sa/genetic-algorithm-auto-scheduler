import { TestBed } from '@angular/core/testing';
import { CanActivateFn } from '@angular/router';

import { timetableGuard } from './timetable.guard';

describe('timetableGuard', () => {
  const executeGuard: CanActivateFn = (...guardParameters) => 
      TestBed.runInInjectionContext(() => timetableGuard(...guardParameters));

  beforeEach(() => {
    TestBed.configureTestingModule({});
  });

  it('should be created', () => {
    expect(executeGuard).toBeTruthy();
  });
});
