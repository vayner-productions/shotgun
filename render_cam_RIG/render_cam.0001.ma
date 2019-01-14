createNode transform -n "render_cam_RIG";
	rename -uid "97D0E042-4B85-B284-066F-268583D44315";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".tx";
	setAttr -l on -k off ".ty";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".rp" -type "double3" 8.8817841970012523e-16 2.4651903288156619e-32 -4.4408920985006262e-16 ;
	setAttr ".sp" -type "double3" 8.8817841970012523e-16 2.4651903288156619e-32 -4.4408920985006262e-16 ;
createNode transform -n "SRT_CON" -p "render_cam_RIG";
	rename -uid "BF3E99DA-4855-4FA9-063D-689951DE41EC";
createNode nurbsCurve -n "SRT_CONShape" -p "SRT_CON";
	rename -uid "8BCC1AB8-49BD-595E-E991-BCB71D94ECBA";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 17;
	setAttr ".cc" -type "nurbsCurve" 
		3 6 2 no 3
		11 -2 -1 0 1 2 3 4 5 6 7 8
		9
		3.1176914536239817 1.1021821192326162e-16 -1.7999999999999972
		-4.4569739092857034e-16 2.2043642384652361e-16 -3.6000000000000005
		-3.117691453623979 1.102182119232618e-16 -1.8000000000000003
		-3.1176914536239799 -1.1021821192326169e-16 1.7999999999999985
		-1.4642331561218943e-15 -2.2043642384652356e-16 3.5999999999999996
		3.1176914536239781 -1.1021821192326191e-16 1.800000000000002
		3.1176914536239817 1.1021821192326162e-16 -1.7999999999999972
		-4.4569739092857034e-16 2.2043642384652361e-16 -3.6000000000000005
		-3.117691453623979 1.102182119232618e-16 -1.8000000000000003
		;
createNode transform -n "rotX_NUL" -p "SRT_CON";
	rename -uid "0C8CE7BB-402D-FF77-1058-C293A9523053";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".tx";
	setAttr -l on -k off ".ty";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".rp" -type "double3" 0 -6.6613381477509392e-16 0 ;
	setAttr ".sp" -type "double3" 0 -6.6613381477509392e-16 0 ;
createNode transform -n "rotX_CON" -p "rotX_NUL";
	rename -uid "0D15E178-42D0-9066-2233-69B1F8039A15";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".tx";
	setAttr -l on -k off ".ty";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode nurbsCurve -n "rotX_CONShape" -p "rotX_CON";
	rename -uid "3B1B2962-4585-8B1D-2745-5498887644A3";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		9.596474681976945e-17 1.5672232497824492 -1.567223249782449
		8.3101253693685115e-33 2.2163883751087754 -1.3571464646221824e-16
		-9.596474681976945e-17 1.5672232497824488 1.567223249782449
		-1.3571464646221829e-16 1.1489796475049661e-16 2.2163883751087763
		-9.596474681976945e-17 -1.567223249782449 1.567223249782449
		-1.3594628955617178e-32 -2.2163883751087767 2.2201713939206452e-16
		9.596474681976945e-17 -1.5672232497824488 -1.567223249782449
		1.3571464646221829e-16 -3.022481001559918e-16 -2.2163883751087763
		9.596474681976945e-17 1.5672232497824492 -1.567223249782449
		8.3101253693685115e-33 2.2163883751087754 -1.3571464646221824e-16
		-9.596474681976945e-17 1.5672232497824488 1.567223249782449
		;
createNode transform -n "rotY_NUL" -p "rotX_CON";
	rename -uid "8FEC0085-4AAB-6ED8-04E4-C086CE3B629D";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".tx";
	setAttr -l on -k off ".ty";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".rp" -type "double3" 4.4408920985006262e-16 1.2325951644078309e-32 -2.2204460492503131e-16 ;
	setAttr ".sp" -type "double3" 4.4408920985006262e-16 1.2325951644078309e-32 -2.2204460492503131e-16 ;
createNode transform -n "rotY_CON" -p "rotY_NUL";
	rename -uid "921818A5-4426-3C0D-7EE0-5B81C3F2949D";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".tx";
	setAttr -l on -k off ".ty";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode nurbsCurve -n "rotY_CONShape" -p "rotY_CON";
	rename -uid "DD5414D6-409D-D01D-7650-598F0175C3F8";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 14;
	setAttr ".cc" -type "nurbsCurve" 
		3 6 2 no 3
		11 -2 -1 0 1 2 3 4 5 6 7 8
		9
		2.0784609690826543 7.3478807948841079e-17 -1.1999999999999982
		-2.9713159395238021e-16 1.4695761589768238e-16 -2.4000000000000004
		-2.0784609690826525 7.3478807948841202e-17 -1.2000000000000002
		-2.0784609690826534 -7.3478807948841141e-17 1.1999999999999991
		-9.7615543741459625e-16 -1.4695761589768238e-16 2.3999999999999999
		2.0784609690826521 -7.3478807948841276e-17 1.2000000000000013
		2.0784609690826543 7.3478807948841079e-17 -1.1999999999999982
		-2.9713159395238021e-16 1.4695761589768238e-16 -2.4000000000000004
		-2.0784609690826525 7.3478807948841202e-17 -1.2000000000000002
		;
createNode transform -n "rotZ_NUL" -p "rotY_CON";
	rename -uid "F308E1E7-4552-4BDF-E1FE-558975725233";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".tx";
	setAttr -l on -k off ".ty";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
	setAttr ".rp" -type "double3" 0 -3.3306690738754696e-16 0 ;
	setAttr ".sp" -type "double3" 0 -3.3306690738754696e-16 0 ;
createNode transform -n "rotZ_CON" -p "rotZ_NUL";
	rename -uid "B302D12C-4CA3-B976-1B68-62AF0A08842E";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".tx";
	setAttr -l on -k off ".ty";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode nurbsCurve -n "rotZ_CONShape" -p "rotZ_CON";
	rename -uid "D99C65DB-48B3-54D6-04DB-AAA1BD7D3C3D";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 6;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		1.567223249782449 1.5672232497824492 0
		1.3571464646221824e-16 2.2163883751087754 0
		-1.567223249782449 1.5672232497824488 0
		-2.2163883751087763 1.1489796475049661e-16 0
		-1.567223249782449 -1.567223249782449 0
		-2.2201713939206452e-16 -2.2163883751087767 0
		1.567223249782449 -1.5672232497824488 0
		2.2163883751087763 -3.022481001559918e-16 0
		1.567223249782449 1.5672232497824492 0
		1.3571464646221824e-16 2.2163883751087754 0
		-1.567223249782449 1.5672232497824488 0
		;
createNode transform -n "render_cam" -p "rotZ_CON";
	rename -uid "B348B185-4E31-7A10-F8DF-E79EDBA9DDB4";
	setAttr -l on -k off ".v";
	setAttr -l on -k off ".tx";
	setAttr -l on -k off ".ty";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr -l on -k off ".sx";
	setAttr -l on -k off ".sy";
	setAttr -l on -k off ".sz";
createNode camera -n "render_camShape" -p "render_cam";
	rename -uid "5D9BD816-4A12-4DDE-A3BE-98B64E830FC6";
	setAttr -k off ".v";
	setAttr ".rnd" no;
	setAttr ".cap" -type "double2" 1.41732 0.94488 ;
	setAttr ".ff" 0;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "camera1";
	setAttr ".den" -type "string" "camera1_depth";
	setAttr ".man" -type "string" "camera1_mask";
	setAttr ".ai_translator" -type "string" "perspective";