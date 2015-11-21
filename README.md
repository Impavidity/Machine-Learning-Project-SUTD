# Machine-Learning-Project-SUTD

## Emission Model

File: emission.py

New an instance:
> model = EmissionEstimate()

Add corpus:
> mode.add_corpus("File_Name")

Test:
> model.test("Test_Name", "Ans_Name")

Accuracy:
> model.accuracy_calc("File_1", "File_2")

##Transition Model

File: transition.py

New an instance:
> model = TransitionEstimate()

Add corpus:
> model.add_corpus("File_Name")

Test:
> model.test("Test_Name", "Ans_Name")

Accuracy:
> model.accuracy_calc("File_1", "File_2")