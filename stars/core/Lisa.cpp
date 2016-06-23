/*
 *  Lisa.cpp
 *  OpenGeoDa
 *
 *  Created by Mark McCann on 1/21/11.
 *  Copyright 2011 ASU. All rights reserved.
 *
 */

#include <stack>
#include <bitset>
#include <vector>
#include "Randik.h"
#include "GalWeight.h"
//#include "GwtWeight.h"
#include "Lisa.h"
#include <iostream>

bool GeodaLisa::LISA(int		nObs,				  // The size of data
					 double*	Data,				  // The input data 
					 GalElement* W,					  // The weight
					 const int numPermutations,		  // The number of permutation
					 std::vector<double>& localMoran, // The LISA
					 double*	sigLocalMoran,	      // The significances
					 int*		sigFlag,			  // The significance category
					 int*		cluster)		      // The Cluster (HH,LL,LH,HL)

{    
	StandardizeData(nObs, Data);	
	OgSet workPermutation(nObs);     
	Randik  rng;

	if (!Data || !sigLocalMoran || ! sigFlag || !W) 
	{
		delete [] sigLocalMoran;
		sigLocalMoran = NULL;
		delete [] sigFlag;
		sigFlag = NULL;
		return false;
	}
	
	for (int cnt= 0; cnt < nObs; ++cnt)  
	{
		const int numNeighbors = W[cnt].Size();
		
		// compute LISA 
		const double Wdata = W[cnt].SpatialLag(Data,true);
		localMoran[cnt] = Data[cnt] * Wdata;
		
		// assign the cluster
		if (Data[cnt] > 0 && Wdata > 0) cluster[cnt] = 1;
		else if (Data[cnt] < 0 && Wdata < 0) cluster[cnt] = 2;
		else if (Data[cnt] > 0 && Wdata < 0) cluster[cnt] = 4;
		else cluster[cnt] = 3;
		
		int countLarger = 0;
		for (int permutation= 0; permutation < numPermutations; ++permutation)  
		{
			int rand= 0;
			while (rand < numNeighbors)  
			{      
				// computing 'perfect' permutation of given size
				const int  newRandom=  (int) (rng.fValue() * nObs);
				if (newRandom != nObs && newRandom != cnt && 
					!workPermutation.Belongs(newRandom))  
				{
					workPermutation.Push(newRandom);
					++rand;
				}
			}
			double permutedLag= 0;
			// use permutation to compute the lag
			// compute the lag for contiguity weights
			for (int cp= 0; cp < numNeighbors; ++cp)
				permutedLag += Data[workPermutation.Pop()];
			
			// row standardization
			if (numNeighbors) permutedLag /= numNeighbors;
			const double localMoranPermuted = Data[cnt] * permutedLag;
			if (localMoranPermuted >= localMoran[cnt]) ++countLarger;
		}
		// pick the smallest
		if (numPermutations-countLarger < countLarger) 
			countLarger= numPermutations-countLarger;
		
		sigLocalMoran[cnt] = (countLarger + 1.0)/(numPermutations+1);
		// 'significance' of local Moran;
		
		if (sigLocalMoran[cnt] <= 0.0001) sigFlag[cnt] = 4;
		else if (sigLocalMoran[cnt] <= 0.001) sigFlag[cnt] = 3;
		else if (sigLocalMoran[cnt] <= 0.01) sigFlag[cnt] = 2;
		else if (sigLocalMoran[cnt] <= 0.05) sigFlag[cnt]= 1;
		else 
		{
			sigFlag[cnt]= 0;
			cluster[cnt] = 0;
		}
		// observations with no neighbors get marked as isolates
		if (numNeighbors == 0) {
			sigFlag[cnt] = 5;
			cluster[cnt] = 5;
		}
	}
	return true;
}


bool GeodaLisa::LISA(int nObs,
					 DataPoint*	RawData,
					 GalElement* W,
					 const int numPermutations,
					 std::vector<double>& localMoran,
					 double* sigLocalMoran,
					 int* sigFlag,
					 int* cluster)
{  
	Randik rng;
	
	if (!RawData || !sigLocalMoran || ! sigFlag || !W) 
	{
		delete [] sigLocalMoran;
		sigLocalMoran = NULL;
		delete [] sigFlag;
		sigFlag = NULL;
		return false;
	}
	
    std::vector<bool> workDict(nObs);
    
	for (int cnt= 0; cnt < nObs; ++cnt)  
	{
		std::stack<int> workPermutation;
        
		// compute LISA 
		localMoran[ cnt ] = RawData[cnt].horizontal * RawData[cnt].vertical;
		if (RawData[cnt].vertical > 0 && RawData[cnt].horizontal > 0) cluster[cnt] = 1;
		else if (RawData[cnt].vertical < 0 && RawData[cnt].horizontal < 0) cluster[cnt] = 2;
		else if (RawData[cnt].vertical < 0) cluster[cnt] = 4;
		else cluster[cnt] = 3; 
		
		
		const int numNeighbors= W[cnt].Size(); // Number of Neighbors
		int	countLarger = 0;                   // for significance
		
		// Start permutation 
		for (int permutation= 0; permutation < numPermutations; ++permutation)  
		{ 
			int		rand= 0; // random number counter
			
			// Draw random numbers for generating unique "cnt"s neighbors
			while (rand < numNeighbors)  
			{      
				// computing 'perfect' permutation of given size
				const int  newRandom=   (int) (rng.fValue() * nObs);
				if (newRandom != nObs && newRandom != cnt && workDict[newRandom] == false)  
				{
					workPermutation.push(newRandom);
                    workDict[newRandom] = true;
					++rand;
				}
			}
			
			double localMoranPermuted, 
			permutedLag= 0;
			// use permutation to compute the lag
			// compute the lag for contiguity weights
			for (int cp= 0; cp < numNeighbors; ++cp) 
            {
				permutedLag += RawData[ workPermutation.top() ].horizontal;
                workPermutation.pop();
			}
            
			// row standardization
			if (numNeighbors) permutedLag /= numNeighbors;
			localMoranPermuted = RawData[ cnt ].horizontal * permutedLag;
			if (localMoranPermuted >= localMoran[cnt]) ++countLarger;
		}
		
		// pick the smallest
		if (numPermutations-countLarger < countLarger) 
			countLarger= numPermutations-countLarger;
		
		sigLocalMoran[cnt] = (countLarger + 1.0)/(numPermutations+1);
		// 'significance' of local Moran;
		if (sigLocalMoran[cnt] <= 0.0001) sigFlag[cnt] = 4;
		else if (sigLocalMoran[cnt] <= 0.001) sigFlag[cnt] = 3;
		else if (sigLocalMoran[cnt] <= 0.01) sigFlag[cnt] = 2;
		else if (sigLocalMoran[cnt] <= 0.05) sigFlag[cnt]= 1;
		else 
		{
			sigFlag[cnt]= 0;
			cluster[cnt] = 0;
		}
		// observations with no neighbors get marked as isolates
		if (numNeighbors == 0) {
			sigFlag[cnt] = 5;
			cluster[cnt] = 5;
		}
	}
	
	return true;
}


bool GeodaLisa::MLISA(int nObs,					// The size of data
					  double* Data1,			// The input data1 
					  double* Data2,			// The input data2 
					  GalElement* W,			// The weight
					  const int	numPermutations, // The number of permutation
					  std::vector<double>& localMoran,	// The LISA
					  double* sigLocalMoran,	// The significances
					  int* sigFlag,				// The significance category
					  int* cluster)				// The Cluster (HH,LL,LH,HL)

{
    /*
	// Data1 and Data2 are assumed standardized
	OgSet workPermutation( nObs );     
	Randik rng;
	
	if (!Data1 || !Data2 || !sigLocalMoran || ! sigFlag || !W) 
	{
		delete [] sigLocalMoran;
		sigLocalMoran = NULL;
		delete [] sigFlag;
		sigFlag = NULL;
		return false;
	}
	
	
	for (int cnt= 0; cnt < nObs; ++cnt)  
	{
		const int numNeighbors = W[cnt].Size();
		
		// compute LISA 
		const double Wdata = W[cnt].SpatialLag(Data2,true);
		localMoran[cnt] = Data1[cnt] * Wdata;
		
		// assign the cluster
		if (cluster != NULL)
		{
			if (Data1[cnt] > 0 && Wdata > 0) cluster[cnt] = 1;
			else if (Data1[cnt] < 0 && Wdata < 0) cluster[cnt] = 2;
			else if (Data1[cnt] > 0 && Wdata < 0) cluster[cnt] = 4;
			else cluster[cnt] = 3;
		}
		
		int countLarger = 0;
		for (int permutation= 0; permutation < numPermutations; ++permutation)  
		{
			int rand= 0;
			while (rand < numNeighbors)  
			{      
				// computing 'perfect' permutation of given size
				const int  newRandom=  (int) (rng.fValue() * nObs);
				if (newRandom != nObs && newRandom != cnt && 
					!workPermutation.Belongs(newRandom))  
				{
					workPermutation.Push(newRandom);
					++rand;
				}
			}
			double permutedLag= 0;
			// use permutation to compute the lag
			// compute the lag for contiguity weights
			for (int cp= 0; cp < numNeighbors; ++cp)
				permutedLag += Data2[workPermutation.Pop()];
			
			// row standardization
			if (numNeighbors) permutedLag /= numNeighbors;
			const double localMoranPermuted = Data1[cnt] * permutedLag;
			if (localMoranPermuted >= localMoran[cnt]) ++countLarger;
		}
		// pick the smallest
		if (numPermutations-countLarger < countLarger) 
			countLarger= numPermutations-countLarger;
		
		sigLocalMoran[cnt] = (countLarger + 1.0)/(numPermutations+1);
		// 'significance' of local Moran;
		
		if (sigLocalMoran[cnt] <= 0.0001) sigFlag[cnt] = 4;
		else if (sigLocalMoran[cnt] <= 0.001) sigFlag[cnt] = 3;
		else if (sigLocalMoran[cnt] <= 0.01) sigFlag[cnt] = 2;
		else if (sigLocalMoran[cnt] <= 0.05) sigFlag[cnt]= 1;
		else 
		{
			sigFlag[cnt]= 0;
			cluster[cnt] = 0;
		}
		// observations with no neighbors get marked as isolates
		if (numNeighbors == 0) {
			sigFlag[cnt] = 5;
			cluster[cnt] = 5;
		}
	}
     */
	return true;
}

bool call_lisa()
{
	return false;
}

int main()
{
	int nObs = 15;
	double data[15] = {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15};
	//GwtWeight* w = new GwtWeight("Data_and_Rates_for_Beats.gwt");
	GalWeight* w = new GalWeight("Data_and_Rates_for_Beats.gal");
	const int numPermutations = 999;
	std::vector<double> localMoran(nObs);
	double* sigLocalMoran = new double[nObs];
	int* sigFlag = new int[nObs];
	int* clusterFlag = new int[nObs];
	GeodaLisa::LISA(nObs, data, w->gal, numPermutations, 
					localMoran, sigLocalMoran, sigFlag, clusterFlag);
	for (int i=0; i<nObs; ++i)
		std::cout<<localMoran[i]<<","<<std::endl;
	return 0;
}
