      program bi207bgd
      dimension ivect(8)

      call cpu_time(T1)
c
      GamInt1=120. ! mm - interaction length, from NIST
      GamEne1=1.064 ! MeV - energy when it comes out of the atom
      Gamfrq1=0.75 ! Frequency i.e. BR

      !this is the gamma at the fundamental state (see decay scheme)
      GamInt2=80. ! mm (from NIST)
      GamEne2=0.57 ! MeV
      Gamfrq2=0.98

      !
      GamInt3=160. ! mm
      GamEne3=1.77 ! MeV
      Gamfrq3=0.069

      !BRs of electrons (upper sections in the Decay table)!
      EleFrq1=0.0703
      EleFrq2=0.0184
      EleFrq3=0.0054
      EleFrq4=0.0152
      EleFrq5=0.0044
      EleFrq6=0.0015
c
      prb1=gamfrq1
      prb2=prb1+gamfrq2
      prb3=prb2+gamfrq3
      prb4=prb3+elefrq1
      prb5=prb4+elefrq2
      prb6=prb5+elefrq3
      prb7=prb6+elefrq4
      prb8=prb7+elefrq5
      prb9=prb8+elefrq6
      print *, prb9
      !prb9 is used for normalization. we don't care
      !about rate. we only care about geometry
c   

      sctmax=0.
      do i=1,8
         ivect(i)=0
      enddo
      pi2=2.*3.1415927
c
      do i=1,1000000
         Aprob=prb9*rndm(x) !normalizing here
         if(Aprob.le.prb1) then
            DInter=GamInt1!mean free path (decay table)
            Energy=GamEne1
            iele=0
         elseif(Aprob.le.prb2) then
            DInter=GamInt2
            Energy=GamEne2
            iele=0
        elseif(Aprob.le.prb3) then
            DInter=GamInt3
            Energy=GamEne3
            iele=0
         elseif(Aprob.le.prb4) then
            DInter=0. !(interaction happens at 0 distance)
            Energy=0.976
            iele=1 !flag 1-> this is an electron
         elseif(Aprob.le.prb5) then
            DInter=0.
            Energy=1.049
            iele=1
         elseif(Aprob.le.prb6) then
            DInter=0.
            Energy=1.060
            iele=1
        elseif(Aprob.le.prb7) then
            DInter=0.
            Energy=0.482
            iele=1
         elseif(Aprob.le.prb8) then
            DInter=0.
            Energy=0.556
            iele=1
         else
            DInter=0.
            Energy=0.566
            iele=1
         endif
c        
         !generating the event position on the source
         !5 mm radius - this is a square
         x0=5.0*rndm(x)-2.5
         y0=5.0*rndm(x)-2.5

         !condition for the circle
         if(x0*x0+y0*y0<6.25) then
            x0=x0+1.
            z0=0.

            !interaction distance
            d=-Dinter*log(rndm(x))

            !direction of the next step
            phi=rndm(x)*pi2
            ctheta=rndm(x)
            stheta=sqrt(1.-ctheta*ctheta)

            !point at which the gamma interacted
            x1=x0+d*stheta*sin(phi)
            y1=y0+d*stheta*cos(phi)
            z1=z0+d*ctheta
            r1=sqrt(x1*x1+y1*y1)

            !cut
            i1=9999
            if(z1.ge.0..and.z1<520.) then

               !selection of the wires
               !checking if that point is within the set
               !of wires or not
               y1p=+x1*0.577+13.164 !mm; 13.164 defines the fiducial volume; 0.577 is the distance between strips (tan of angle)
               y1m=+x1*0.577-13.164
               y2p=-x1*0.577+13.164
               y2m=-x1*0.577-13.164


               !condition for the generated particle to be inside the exagonal tower given by Induction strip 1 and 2 xmin,xmax, ymin,ymax
               if(y1>y1m.and.
     $            y1<y1p.and.
     $            y1>y2m.and.
     $            y1<y2p.and.
     $            x1>-20.and.
     $            x1<+20) then
c                 translating into strip number
                  i1=(x1+20.)/5.+1
                  !things stored into a integer variable are integer
c                 if(i1.gt.6) print *,x1, i1

                  !Compton
                  if(iele.eq.0) then
                     iflg=0
                     gg=Energy/0.511
                     do while(iflg.eq.0)
                        ct=2.*rndm(x)-1.
                        eps=1./(1.+gg*(1.-ct))
                        sctprob=0.5*eps**2*(eps+1./eps-(1.-ct**2))
c                        sctprob=0.5*(1.+ct*ct)
c                        if(sctmax.lt.sctprob) then
c                           sctmax=sctprob
c                  print *,energy,ct,eps,eps**2,1./eps, 1-ct**2, sctprob
c                        endif
                        if(rndm(x).le.sctprob) then
                           iflg=1
                           ComptE=Energy*(1.-1./(1.+gg*(1-ct)))
                        endif
                     enddo
                  else
                     !energy of the scattered electron
                     ComptE=Energy
                     !spreading a bit according to the resolution
                     if(rndm(x).le.0.33) ComptE=ComptE*rndm(x)
                  endif
c
                  ! generation a random number from a
                  ! gaussian distribution
                  ! central limit theorem
                  res=0.
                  !only works if this is 12
                  Do k=1,12
                     res=res+rndm(x)
                  Enddo

                  res=0.07*(res-6.) !0.07 is the resolution
                  !for the 1 MeV (1063 keV) only. other decays
                  !have different resolutions. All come from data
                  !We could add a square root factor of the energy

                  rr=comptE+res !final energy (see res definition)
c
                  print *, i,d,x1,y1,z1,i1,energy,compte,rr

                  !gaussian distributed threshold
                  rth=0.                 
                  Do k=1,12
                     rth=rth+rndm(x)
                  Enddo
                  rth=0.09*(rth-6.) !this is the normalization
                  !to a threshold of 90 keV
                  !simulates noise

c                 printing one file per strip
c                 considering 8 strips: 3 + 3 + 2
                  if(ComptE.gt.(.32+rth)) then
                  if(i1.eq.1) write(91,*) iele,compte,rr
                  if(i1.eq.2) write(92,*) iele,compte,rr
                  if(i1.eq.3) write(93,*) iele,compte,rr
                  if(i1.eq.4) write(94,*) iele,compte,rr
                  if(i1.eq.5) write(95,*) iele,compte,rr
                  if(i1.eq.6) write(96,*) iele,compte,rr
                  if(i1.eq.7) write(97,*) iele,compte,rr
                  if(i1.eq.8) write(98,*) iele,compte,rr
                  endif
                  if(i1>0.and.i1<9) ivect(i1)=ivect(i1)+1
               endif
            endif
c
         endif
      enddo
      print *,ivect

      call cpu_time(T2)
      print *, " "
      print *, 'Execution time: ', T2-T1, 's'

      end
      
         
! to compile: gfortran -o o.out bi207bg.f `cernlib graflib`
! to run: ./o.out
