import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TimetableDetailsComponent } from './timetable-details.component';

describe('TimetableDetailsComponent', () => {
  let component: TimetableDetailsComponent;
  let fixture: ComponentFixture<TimetableDetailsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TimetableDetailsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TimetableDetailsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
