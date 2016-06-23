/* This is an interface file for the random generator class.
Class Randik designed to generate float psudo-random numbers 0 <= x < 1.
Knuth, Donald E. 1981. The Art.., vol 2, 3.2-3.3.
*/

#ifndef __RANDIKINCLUDED__
#define __RANDIKINCLUDED__

class Randik
{
public:
    Randik();
    virtual ~Randik();
    float fValue() { // return float random value from [0, 1)
		Iterate();
		const float FC = (float) 1.0/MBIG;
		return cohort[current] * FC;
    }
    long lValue() { // return int random from 0 to MBIG-1
		Iterate();
		return cohort[current];
    }
    int* Perm(const int size);    // return random permutation of 1...size
	void PermG(const int size, int* thePermutation);  
private:
    enum {
        cohortStep = 21,
        cohortSize = 55,
        MBIG  = 1000000000,
        MSEED = 161803398,
    } constants;
    int    current;
    long*  cohort;
    void Initialize(const long Seed);   // seed the RNG
    void Iterate();                     // next number
};

#endif
