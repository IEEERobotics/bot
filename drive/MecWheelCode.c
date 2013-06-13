#include <math.h>
#define PI 3.14159265

void DirectionFunction(angle, speed, RSpeed) {
  //pass angle in degrees
	/*
	Wheel A = front left
	Wheel B = front Right
	Wheel C = Back Left
	Wheel D = Back Right
	*/
	//voltage multipliers based on previous derivations:
	Va = speed * sin(angle*PI/180 + PI/4) + Rspeed;
	Vb = speed * cos(angle*PI/180 + PI/4) - Rspeed;
	Vc = speed * cos(angle*Pi/180 + PI/4) + Rspeed;
	Vd = speed * sin(angle*Pi/180 + PI/4) - Rspeed;
		
	//pass voltage to output, find out how to do that.

}
