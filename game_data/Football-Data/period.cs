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
			int val = 1;
			int.TryParse(Input, out val);
			Output = val.ToNth();

			// Define the file path where you want to write the output.
			string filePath = "C:/Users/PCTech/Documents/Graphics Outfitters/Football-Data/period.txt";

			// Write the Output to the text file.
			File.WriteAllText(filePath, Output);
			return Output; //This is the value that will be outputted
		}
	}

	public static class Extensions
	{
		public static string ToNth(this int input, int numOfPeriods = int.MaxValue)
		{
			if (input == numOfPeriods + 1)
				return "OT";
			if (input > numOfPeriods)
				return (input - numOfPeriods) + "OT";
			return input + ((input / 10 == 1)
			? "th" : (input % 10 == 1)
			? "st" : (input % 10 == 2)
			? "nd" : (input % 10 == 3)
			? "rd" : "th");
		}
	}
}