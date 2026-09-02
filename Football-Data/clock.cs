using System;
using System.IO; // Import the System.IO namespace
namespace UserScript
{
	using System;
	public class RunScript
	{
		//USERS SHOULD NOT CHANGE THIS CODE UNDER MOST CIRCUMSTANCES
		//`Input` is the value set by ScoreBridge that you will use to condition the output.
		private string Input = "";
		public void SetRead(string Value)
		{
			Input = Value;     //Should Not Change!
		}

		//USERS SHOULD MAKE CHANGES HERE
		public string Eval()
		{
			//Sample Logic:
			string Output;
			//string val = "";
			//int.TryParse(Input, out val);
			Output = Input;

			// Define the file path where you want to write the output.
			string filePath = "C:/Users/PCTech/Documents/Graphics Outfitters/Football-Data/clock.txt";

			// Write the Output to the text file.
			File.WriteAllText(filePath, Output);
			return Output; //This is the value that will be outputted
		}
	}
}