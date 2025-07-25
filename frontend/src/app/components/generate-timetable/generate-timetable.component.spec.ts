import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GenerateTimetableComponent } from './generate-timetable.component';

describe('GenerateTimetableComponent', () => {
  let component: GenerateTimetableComponent;
  let fixture: ComponentFixture<GenerateTimetableComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GenerateTimetableComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GenerateTimetableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
