using System;
using System.IO; // Import the System.IO namespace
namespace UserScript
{
	using System;

	/* The script module allows you to take the value that would normally be sent to the output *
	* and make changes to it before it reaches the output method. *
	* This enables users to make simple or complex conditions to better suite needs. *
	* *
	* It can be used to translate serial values that come in as 1 or 0 boolean and translate *
	* it to something readable on different platforms like True or False. *
	* *
	* Alternatively it could be used to replace images in systems like Tri-caster, using *
	* the result of the possession indicator could swap images out using the Datalink feed. */

	public class RunScript
	{
		//USERS SHOULD NOT CHANGE THIS CODE UNDER MOST CIRCUMSTANCES

		//`Input` is the value set by ScoreBridge that you will use to condition the output.
		private string Input = "";
		public void SetRead(string Value)
		{
			Input = Value; //Should Not Change!
		}

		//USERS SHOULD MAKE CHANGES HERE
		public string Eval()
		{
			//Sample Logic:
			int val = 1;
			int.TryParse(Input, out val);

			Output = val.ToNth();

			// Define the file path where you want to write the output.
			string filePath = "C:/Users/PCTech/Documents/Graphics Outfitters/Football-Data/clock.txt";

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
			? "TH" : (input % 10 == 1)
			? "ST" : (input % 10 == 2)
			? "ND" : (input % 10 == 3)
			? "RD" : "TH");

		}

		public static string downToText(this int input)
		{
			if (input == "1")
				return "First & ";
			if (input == "2")
				return "Second & ";
			if (input == "3")
				return "Third & ";
			if (input == "4")
				return "Fourth & ";
		}

		public statis string quarterToText(this int input)
		{
			if (input == "1")
				return "1st";
			if (input == "2")
				return "2nd";
			if (input == "3")
				return "3rd";
			if (input == "4")
				return "4th";

			return "OT";
		}

		public static string possession(this int input)

	}
}