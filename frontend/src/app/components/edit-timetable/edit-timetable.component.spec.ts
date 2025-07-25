import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditTimetableComponent } from './edit-timetable.component';

describe('EditTimetableComponent', () => {
  let component: EditTimetableComponent;
  let fixture: ComponentFixture<EditTimetableComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EditTimetableComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EditTimetableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
