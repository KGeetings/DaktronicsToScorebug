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
			Output = val.ToString();

			if (!int.TryParse(Input, out val) ||val < 0 || val > 3)
			{
				val = 0;
			}

			if(File.ReadAllText("C:/Users/PCTech/Documents/Graphics Outfitters/Football-Data/homeTOL.txt") == Output)
			{
				return Output;
			}

			string sourceFile = "";
			switch (val)
			{
				case 0:
					sourceFile = "C:/Users/PCTech/Documents/Graphics Outfitters/Football-Data/Timeout-0.png";
					break;
				case 1:
					sourceFile = "C:/Users/PCTech/Documents/Graphics Outfitters/Football-Data/Timeout-1.png";
					break;
				case 2:
					sourceFile = "C:/Users/PCTech/Documents/Graphics Outfitters/Football-Data/Timeout-2.png";
					break;
				case 3:
					sourceFile = "C:/Users/PCTech/Documents/Graphics Outfitters/Football-Data/Timeout-3.png";
					break;
			}
			string destinationFile = "C:/Users/PCTech/Documents/Graphics Outfitters/Football-Data/homeTOL.png";

			try
			{
				File.Copy(sourceFile, destinationFile, true);
				File.SetLastWriteTime(destinationFile, DateTime.Now);	//Overwrites the file's write time so OBS sees it changed
			}
			catch (Exception ex)
			{
				return "Error updating image";
			}
			File.WriteAllText("C:/Users/PCTech/Documents/Graphics Outfitters/Football-Data/homeTOL.txt", Output);
			return Output; //This is the value that will be outputted
		}
	}
}