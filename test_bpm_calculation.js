// Test BPM calculation logic
function testBpmCalculation() {
    console.log("Testing BPM calculation logic...");
    
    const testCases = [
        { bpm: 120, beats: 2, originalDuration: 1000 },
        { bpm: 60, beats: 2, originalDuration: 1000 },
        { bpm: 240, beats: 2, originalDuration: 1000 },
        { bpm: 120, beats: 4, originalDuration: 1000 },
        { bpm: 120, beats: 1, originalDuration: 1000 }
    ];
    
    testCases.forEach((test, index) => {
        const targetDuration = (test.beats / test.bpm) * 60000;
        const speedMultiplier = test.originalDuration / targetDuration;
        
        console.log(`Test ${index + 1}:`);
        console.log(`  BPM: ${test.bpm}, Beats: ${test.beats}, Original Duration: ${test.originalDuration}ms`);
        console.log(`  Target Duration: ${targetDuration.toFixed(0)}ms`);
        console.log(`  Speed Multiplier: ${speedMultiplier.toFixed(2)}x`);
        console.log(`  Expected: ${test.bpm === 120 ? '1.0x' : test.bpm > 120 ? 'faster' : 'slower'}`);
        console.log('');
    });
}

// Run the test
testBpmCalculation(); 