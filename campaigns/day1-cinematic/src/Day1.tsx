import React from 'react';
import {AbsoluteFill, interpolate, Sequence, useCurrentFrame, useVideoConfig} from 'remotion';

const BG='#050708', IV='#F1EFE5', CY='#49D4D0';
const Beat: React.FC<{from:number; dur:number; title:string; sub?:string}> = ({from,dur,title,sub}) => {
  const frame=useCurrentFrame();
  const local=frame-from;
  const opacity=interpolate(local,[0,8,dur-8,dur],[0,1,1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
  return <Sequence from={from} durationInFrames={dur}><AbsoluteFill style={{background:BG,color:IV,fontFamily:'Inter',justifyContent:'center',padding:80,opacity}}>
    <div style={{position:'absolute',left:42,top:80,bottom:80,width:4,background:CY}} />
    <div style={{fontSize:66,fontWeight:700,lineHeight:1.02,letterSpacing:-2}}>{title}</div>
    {sub && <div style={{fontSize:28,color:CY,marginTop:28}}>{sub}</div>}
  </AbsoluteFill></Sequence>;
};
export const Day1: React.FC = () => {
  const fps=30; return <AbsoluteFill style={{background:BG}}>
    <Beat from={0} dur={2*fps} title="कौन सा सिस्टम?" sub="17 TABS • 4 DASHBOARDS • 3 PHONES" />
    <Beat from={2*fps} dur={4*fps} title="AUTOMATION." sub="Apparently." />
    <Beat from={6*fps} dur={4*fps} title="11:47 PM" sub="YOUR SYSTEM SLEPT." />
    <Beat from={10*fps} dur={5*fps} title="EVERYTHING IS CONNECTED." sub="EXCEPT THE WORK." />
    <Beat from={15*fps} dur={4*fps} title="समस्या लोगों की नहीं है।" sub="समस्या है कार्रवाई की।" />
    <Beat from={19*fps} dur={6*fps} title="UNDERSTAND → REMEMBER" sub="DECIDE → ACT → VERIFY" />
    <Beat from={25*fps} dur={4*fps} title="LUXOR9" sub="INSTITUTIONAL INTELLIGENCE. BUILT TO EXECUTE." />
    <Beat from={29*fps} dur={4*fps} title="KNOW. THINK. ACT." sub="PROVE. LEARN." />
    <Beat from={33*fps} dur={2*fps} title="INTELLIGENCE → EXECUTION" sub="अब सिर्फ एआई से बात मत कीजिए. उससे काम करवाइए." />
  </AbsoluteFill>;
};
