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
			Output = val.downToText();

			// Define the file path where you want to write the output.
			string filePath = "C:/Users/PCTech/Documents/Graphics Outfitters/Football-Data/down.txt";

			if (File.ReadAllText(filePath) == Output || Output == null || Output == "")
			{
				return Output;
			}

			// Write the Output to the text file.
			File.WriteAllText(filePath, Output);
			return Output; //This is the value that will be outputted
		}
	}

	public static class Extensions
	{
		public static string downToText(this int input)
		{
			if (input == 1)
				return "1st & ";
			if (input == 2)
				return "2nd & ";
			if (input == 3)
				return "3rd & ";
			if (input == 4)
				return "4th & ";
			return "";
		}
	}
}