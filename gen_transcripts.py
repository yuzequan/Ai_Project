import json

data = {
    "fields": ["关联场次","speaker_id","speaker_role","content","start_time","end_time","is_teacher"],
    "rows": [
        [[{"id":"recvq5KPorfw0C"}],"teacher_101","teacher","Hello everyone, today we will learn the basic concepts of CBT. The core of CBT lies in the relationship between cognition, emotion, and behavior.","2026-07-15 09:02:00","2026-07-15 09:05:00",True],
        [[{"id":"recvq5KPorfw0C"}],"teacher_101","teacher","Cognition determines emotion and behavior. This is the most important core concept of CBT. Everyone must remember the cognitive triangle model.","2026-07-15 09:05:00","2026-07-15 09:08:00",True],
        [[{"id":"recvq5KPorfw0C"}],"stu_001","student","Teacher, can you explain automatic thoughts again?","2026-07-15 09:08:00","2026-07-15 09:09:00",False],
        [[{"id":"recvq5KPorfw0C"}],"teacher_101","teacher","Sure. Automatic thoughts are ideas that our brain quickly and automatically generates in specific situations, usually unconscious.","2026-07-15 09:09:00","2026-07-15 09:12:00",True],
        [[{"id":"recvq5KPorfw0C"}],"teacher_101","teacher","For example, if you fail an exam, the automatic thought might be 'I am stupid', which is a manifestation of cognitive distortion.","2026-07-15 09:12:00","2026-07-15 09:15:00",True],
        [[{"id":"recvq5KPorfw0C"}],"stu_002","student","I see. How should we change this kind of thinking?","2026-07-15 09:15:00","2026-07-15 09:16:00",False],
        [[{"id":"recvq5KPorfw0C"}],"teacher_101","teacher","This involves cognitive restructuring techniques. We need to identify negative thoughts, challenge them, and replace them with more reasonable ideas.","2026-07-15 09:16:00","2026-07-15 09:20:00",True],
        [[{"id":"recvq5KPorChSY"}],"teacher_102","teacher","Hello everyone, today we continue to explore the cognitive triangle model. How do thoughts, emotions, and behaviors interact?","2026-07-15 14:01:00","2026-07-15 14:05:00",True],
        [[{"id":"recvq5KPorChSY"}],"teacher_102","teacher","When we have negative thoughts, it triggers negative emotions, which in turn leads to negative behaviors. This is a vicious cycle.","2026-07-15 14:05:00","2026-07-15 14:08:00",True],
        [[{"id":"recvq5KPorChSY"}],"stu_004","student","Teacher, how can we break this negative cycle?","2026-07-15 14:08:00","2026-07-15 14:09:00",False],
        [[{"id":"recvq5KPorChSY"}],"teacher_102","teacher","Great question. We can start from any link, but the most effective is to start from thoughts and change cognition.","2026-07-15 14:09:00","2026-07-15 14:12:00",True],
        [[{"id":"recvq5KPorChSY"}],"teacher_102","teacher","Through cognitive restructuring, we can learn to identify and challenge unreasonable ideas, thereby changing emotions and behaviors.","2026-07-15 14:12:00","2026-07-15 14:15:00",True],
        [[{"id":"recvq5KPorfwdW"}],"teacher_103","teacher","Today we will discuss automatic thoughts. Does anyone know what automatic thoughts are?","2026-07-16 09:05:00","2026-07-16 09:08:00",True],
        [[{"id":"recvq5KPorfwdW"}],"stu_007","student","Are they the ideas that appear in our minds without thinking?","2026-07-16 09:08:00","2026-07-16 09:09:00",False],
        [[{"id":"recvq5KPorfwdW"}],"teacher_103","teacher","Exactly! Automatic thoughts have three characteristics: fast speed, automation, and habituality.","2026-07-16 09:09:00","2026-07-16 09:12:00",True],
        [[{"id":"recvq5KPorfwdW"}],"teacher_103","teacher","Common types include self-negation, excessive judgment of others, catastrophic predictions, hopelessness, and excessive self-blame.","2026-07-16 09:12:00","2026-07-16 09:16:00",True],
        [[{"id":"recvq5KPorMptH"}],"teacher_101","teacher","Today we will talk about cognitive distortions. Cognitive distortions refer to our misinterpretations and judgments of reality.","2026-07-16 14:00:00","2026-07-16 14:04:00",True],
        [[{"id":"recvq5KPorMptH"}],"teacher_101","teacher","There are eight common cognitive distortions: all-or-nothing, catastrophizing, overgeneralization, mental filter, mind reading, labeling, personalization, and should statements.","2026-07-16 14:04:00","2026-07-16 14:08:00",True],
        [[{"id":"recvq5KPorMptH"}],"stu_010","student","Teacher, can you give an example of catastrophizing?","2026-07-16 14:08:00","2026-07-16 14:09:00",False],
        [[{"id":"recvq5KPorMptH"}],"teacher_101","teacher","For example, thinking your career is over because of one failed speech. This is typical catastrophic thinking.","2026-07-16 14:09:00","2026-07-16 14:12:00",True],
        [[{"id":"recvq5KPorlogM"}],"teacher_104","teacher","Today we continue with cognitive distortions. Core beliefs are deep, stable, global self-perceptions, usually formed in childhood.","2026-07-17 09:00:00","2026-07-17 09:04:00",True],
        [[{"id":"recvq5KPorlogM"}],"teacher_104","teacher","Core beliefs are divided into helpless type and unlovable type. Helpless type thinks 'I am incompetent', unlovable type thinks 'I am unlovable'.","2026-07-17 09:04:00","2026-07-17 09:08:00",True],
        [[{"id":"recvq5KPorlogM"}],"stu_013","student","Then what are intermediate beliefs?","2026-07-17 09:08:00","2026-07-17 09:09:00",False],
        [[{"id":"recvq5KPorlogM"}],"teacher_104","teacher","Intermediate beliefs are the bridge connecting core beliefs and automatic thoughts, including attitudes, rules, and assumptions.","2026-07-17 09:09:00","2026-07-17 09:12:00",True],
        [[{"id":"recvq5KPormAjI"}],"teacher_102","teacher","Today we learn cognitive restructuring techniques. Cognitive restructuring has four steps: identify, record, challenge, and replace.","2026-07-17 14:03:00","2026-07-17 14:07:00",True],
        [[{"id":"recvq5KPormAjI"}],"teacher_102","teacher","Evidence testing requires us to ask: What is the evidence supporting this idea? What is the evidence against it?","2026-07-15 14:07:00","2026-07-17 14:11:00",True],
        [[{"id":"recvq5KPormAjI"}],"stu_016","student","Is alternative thinking about replacing negative thoughts with more reasonable ones?","2026-07-17 14:11:00","2026-07-17 14:12:00",False],
        [[{"id":"recvq5KPormAjI"}],"teacher_102","teacher","Exactly! Alternative thinking must be based on evidence, not blind optimism.","2026-07-17 14:12:00","2026-07-17 14:15:00",True],
        [[{"id":"recvq5KPoro6Eg"}],"teacher_103","teacher","Today we discuss behavioral intervention techniques. Behavioral activation is suitable for depression patients, improving mood by increasing positive activities.","2026-07-18 09:00:00","2026-07-18 09:04:00",True],
        [[{"id":"recvq5KPoro6Eg"}],"teacher_103","teacher","Exposure therapy is suitable for anxiety disorders. Key principles are safety, gradual progression, and cognitive processing.","2026-07-18 09:04:00","2026-07-18 09:08:00",True],
        [[{"id":"recvq5KPoro6Eg"}],"stu_019","student","Teacher, will exposure therapy make people more anxious?","2026-07-18 09:08:00","2026-07-18 09:09:00",False],
        [[{"id":"recvq5KPoro6Eg"}],"teacher_103","teacher","It might in the short term, but in the long run anxiety will gradually decrease, eventually reaching habituation.","2026-07-18 09:09:00","2026-07-18 09:12:00",True],
        [[{"id":"recvq5KPorRKDS"}],"teacher_101","teacher","Today we learn Socratic questioning. This is a technique that guides people to discover cognitive errors through questioning.","2026-07-18 14:10:00","2026-07-18 14:14:00",True],
        [[{"id":"recvq5KPorRKDS"}],"teacher_101","teacher","The six core questions include: What is the evidence? Are there other explanations? What is the worst case scenario?","2026-07-18 14:14:00","2026-07-18 14:18:00",True],
        [[{"id":"recvq5KPorRKDS"}],"stu_022","student","How should I fill out the thought record?","2026-07-18 14:18:00","2026-07-18 14:19:00",False],
        [[{"id":"recvq5KPorRKDS"}],"teacher_101","teacher","The thought record has five parts: situation, automatic thought, emotion, alternative thought, and re-evaluated emotion.","2026-07-18 14:19:00","2026-07-18 14:22:00",True],
        [[{"id":"recvq5KPor32LI"}],"teacher_104","teacher","Today we learn coping cards and behavioral experiments. Coping cards are portable cognitive restructuring tools.","2026-07-19 09:01:00","2026-07-19 09:05:00",True],
        [[{"id":"recvq5KPor32LI"}],"teacher_104","teacher","Behavioral experiment five steps: identify negative prediction, design experiment, execute experiment, record results, and update beliefs.","2026-07-19 09:05:00","2026-07-19 09:09:00",True],
        [[{"id":"recvq5KPor32LI"}],"stu_025","student","How should I build my personal psychological toolbox?","2026-07-19 09:09:00","2026-07-19 09:10:00",False],
        [[{"id":"recvq5KPor32LI"}],"teacher_104","teacher","Record the techniques and insights from each practice, gradually forming your own psychological regulation toolbox.","2026-07-19 09:10:00","2026-07-19 09:13:00",True],
        [[{"id":"recvq5KPormhhy"}],"teacher_102","teacher","In the last class, we integrate all CBT techniques. Remember the 10-minute rule: pause for 10 minutes before making a decision.","2026-07-19 14:00:00","2026-07-19 14:04:00",True],
        [[{"id":"recvq5KPormhhy"}],"teacher_102","teacher","Three-stage path: awareness period identifies problems, practice period trains repeatedly, integration period achieves mastery.","2026-07-19 14:04:00","2026-07-19 14:08:00",True],
        [[{"id":"recvq5KPormhhy"}],"stu_028","student","Teacher, what are the boundaries of self-regulation?","2026-07-19 14:08:00","2026-07-19 14:09:00",False],
        [[{"id":"recvq5KPormhhy"}],"teacher_102","teacher","If symptoms are severe or persist for a long time, you must seek professional help in time. Do not tough it out.","2026-07-19 14:09:00","2026-07-19 14:12:00",True],
    ]
}

with open('./ai-monitor-app/data_transcripts.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)

print("Done")
