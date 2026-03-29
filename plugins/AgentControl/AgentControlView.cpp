#include "AgentControlView.h"

#include <QDateTime>
#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QHBoxLayout>
#include <QVBoxLayout>
#include <QLabel>
#include <QPushButton>
#include <QStandardPaths>

#include "AgentControl.h"

namespace lmms::gui
{

AgentControlView::AgentControlView( AgentControlPlugin *plugin )
	: ToolPluginView( plugin )
	, m_plugin( plugin )
	, m_input( new QLineEdit( this ) )
	, m_log( new QTextEdit( this ) )
	, m_status( new QLabel( tr( "Listening on 127.0.0.1:7777" ), this ) )
	, m_voiceStartButton( new QPushButton( tr( "Start Voice" ), this ) )
	, m_voiceStopButton( new QPushButton( tr( "Stop + Run" ), this ) )
	, m_voiceRecordProcess( nullptr )
{
	setWindowTitle( tr( "Agent Control" ) );
	setSizePolicy( QSizePolicy::Fixed, QSizePolicy::Fixed );
	m_log->setReadOnly( true );
	m_input->setPlaceholderText( tr( "Try: import kick.wav or add 808" ) );

	auto runBtn = new QPushButton( tr( "Run" ), this );
	auto layout = new QVBoxLayout( this );
	layout->addWidget( m_status );
	auto row = new QHBoxLayout();
	row->addWidget( m_input );
	row->addWidget( runBtn );
	layout->addLayout( row );
	auto voiceRow = new QHBoxLayout();
	voiceRow->addWidget( m_voiceStartButton );
	voiceRow->addWidget( m_voiceStopButton );
	layout->addLayout( voiceRow );
	layout->addWidget( m_log );

	connect( runBtn, &QPushButton::clicked, this, &AgentControlView::runCommand );
	connect( m_input, &QLineEdit::returnPressed, this, &AgentControlView::runCommand );
	connect( m_voiceStartButton, &QPushButton::clicked, this, &AgentControlView::startVoiceCapture );
	connect( m_voiceStopButton, &QPushButton::clicked, this, &AgentControlView::stopVoiceCapture );
	connect( m_plugin, &AgentControlPlugin::logMessage, this, &AgentControlView::appendLog );
	connect( m_plugin, &AgentControlPlugin::commandResult, this, &AgentControlView::appendLog );
	setVoiceUiState( false );
	appendLog( tr( "Voice: ffmpeg=%1 whisper=%2 mic=%3" )
		.arg( ffmpegPath() )
		.arg( whisperPath() )
		.arg( microphoneDevice() ) );

	hide();
	if( parentWidget() )
	{
		parentWidget()->hide();
	}
}

void AgentControlView::runCommand()
{
	const QString text = m_input->text().trimmed();
	if( text.isEmpty() )
	{
		appendLog( tr( "No command entered" ) );
		return;
	}
	const QString result = m_plugin->handleCommand( text );
	appendLog( text + " => " + result );
	m_input->clear();
}

void AgentControlView::appendLog( const QString &text )
{
	m_log->append( text );
}

void AgentControlView::setVoiceUiState( bool recording )
{
	m_voiceStartButton->setEnabled( !recording );
	m_voiceStopButton->setEnabled( recording );
	if( recording )
	{
		m_status->setText( tr( "Recording voice command..." ) );
	}
	else
	{
		m_status->setText( tr( "Listening on 127.0.0.1:7777" ) );
	}
}

QString AgentControlView::ffmpegPath() const
{
	const QString value = qEnvironmentVariable( "LMMS_FFMPEG_BIN" );
	return value.isEmpty() ? QStringLiteral( "ffmpeg" ) : value;
}

QString AgentControlView::whisperPath() const
{
	const QString value = qEnvironmentVariable( "LMMS_WHISPER_CLI" );
	return value.isEmpty() ? QStringLiteral( "whisper-cli" ) : value;
}

QString AgentControlView::microphoneDevice() const
{
#if defined( Q_OS_MACOS )
	const QString fallback = QStringLiteral( "0" );
#else
	const QString fallback = QStringLiteral( "default" );
#endif
	const QString value = qEnvironmentVariable( "LMMS_MIC_DEVICE" );
	return value.isEmpty() ? fallback : value;
}

QStringList AgentControlView::ffmpegCaptureArgs( const QString &outputPath ) const
{
	QStringList args;
	args << QStringLiteral( "-hide_banner" )
		<< QStringLiteral( "-loglevel" ) << QStringLiteral( "error" );
#if defined( Q_OS_MACOS )
	args << QStringLiteral( "-f" ) << QStringLiteral( "avfoundation" )
		<< QStringLiteral( "-i" ) << QStringLiteral( ":" ) + microphoneDevice();
#elif defined( Q_OS_LINUX )
	args << QStringLiteral( "-f" ) << QStringLiteral( "pulse" )
		<< QStringLiteral( "-i" ) << microphoneDevice();
#else
	args << QStringLiteral( "-f" ) << QStringLiteral( "avfoundation" )
		<< QStringLiteral( "-i" ) << QStringLiteral( ":" ) + microphoneDevice();
#endif
	args << QStringLiteral( "-ac" ) << QStringLiteral( "1" )
		<< QStringLiteral( "-ar" ) << QStringLiteral( "16000" )
		<< QStringLiteral( "-y" ) << outputPath;
	return args;
}

void AgentControlView::startVoiceCapture()
{
	if( m_voiceRecordProcess != nullptr )
	{
		appendLog( tr( "Voice capture is already running" ) );
		return;
	}

	const QString tempDir = QStandardPaths::writableLocation( QStandardPaths::TempLocation );
	if( tempDir.isEmpty() )
	{
		appendLog( tr( "Voice capture failed: no temp directory" ) );
		return;
	}
	m_voiceAudioPath = QDir( tempDir ).filePath(
		QStringLiteral( "lmms_agent_voice_%1.wav" )
			.arg( QDateTime::currentMSecsSinceEpoch() ) );

	m_voiceRecordProcess = new QProcess( this );
	connect( m_voiceRecordProcess,
		QOverload<QProcess::ProcessError>::of( &QProcess::errorOccurred ),
		this,
		&AgentControlView::voiceProcessError );

	const QString ffmpeg = ffmpegPath();
	m_voiceRecordProcess->start( ffmpeg, ffmpegCaptureArgs( m_voiceAudioPath ) );
	if( !m_voiceRecordProcess->waitForStarted( 1500 ) )
	{
		appendLog( tr( "Voice capture failed: could not start %1" ).arg( ffmpeg ) );
		m_voiceRecordProcess->deleteLater();
		m_voiceRecordProcess = nullptr;
		m_voiceAudioPath.clear();
		setVoiceUiState( false );
		return;
	}

	appendLog( tr( "Voice recording started. Click Stop + Run when done." ) );
	setVoiceUiState( true );
}

void AgentControlView::stopVoiceCapture()
{
	if( m_voiceRecordProcess == nullptr )
	{
		appendLog( tr( "Voice capture is not running" ) );
		setVoiceUiState( false );
		return;
	}

	if( m_voiceRecordProcess->state() != QProcess::NotRunning )
	{
		m_voiceRecordProcess->write( "q\n" );
		m_voiceRecordProcess->closeWriteChannel();
		if( !m_voiceRecordProcess->waitForFinished( 2500 ) )
		{
			m_voiceRecordProcess->terminate();
			if( !m_voiceRecordProcess->waitForFinished( 1500 ) )
			{
				m_voiceRecordProcess->kill();
				m_voiceRecordProcess->waitForFinished( 1000 );
			}
		}
	}

	const QString ffmpegErrors = QString::fromUtf8( m_voiceRecordProcess->readAllStandardError() ).trimmed();
	if( !ffmpegErrors.isEmpty() )
	{
		appendLog( tr( "ffmpeg: %1" ).arg( ffmpegErrors ) );
	}

	m_voiceRecordProcess->deleteLater();
	m_voiceRecordProcess = nullptr;
	setVoiceUiState( false );

	const QFileInfo audioInfo( m_voiceAudioPath );
	if( !audioInfo.exists() || audioInfo.size() <= 0 )
	{
		appendLog( tr( "Voice capture failed: no audio recorded" ) );
		m_voiceAudioPath.clear();
		return;
	}

	appendLog( tr( "Transcribing voice command..." ) );
	const QString audioPath = m_voiceAudioPath;
	m_voiceAudioPath.clear();
	if( !runWhisperAndDispatch( audioPath ) )
	{
		appendLog( tr( "Voice command failed" ) );
	}
	QFile::remove( audioPath );
	QFile::remove( audioPath + QStringLiteral( ".txt" ) );
}

bool AgentControlView::runWhisperAndDispatch( const QString &audioPath )
{
	QProcess whisperProcess;
	whisperProcess.start( whisperPath(),
		QStringList{
			QStringLiteral( "-f" ), audioPath,
			QStringLiteral( "-otxt" ),
			QStringLiteral( "-nt" ) } );
	if( !whisperProcess.waitForStarted( 2000 ) )
	{
		appendLog( tr( "Could not start %1. Set LMMS_WHISPER_CLI." ).arg( whisperPath() ) );
		return false;
	}
	if( !whisperProcess.waitForFinished( 60000 ) )
	{
		whisperProcess.kill();
		whisperProcess.waitForFinished( 1000 );
		appendLog( tr( "Whisper timed out" ) );
		return false;
	}

	QString transcript = QString::fromUtf8( whisperProcess.readAllStandardOutput() ).trimmed();
	if( transcript.isEmpty() )
	{
		QFile transcriptFile( audioPath + QStringLiteral( ".txt" ) );
		if( transcriptFile.open( QIODevice::ReadOnly | QIODevice::Text ) )
		{
			transcript = QString::fromUtf8( transcriptFile.readAll() ).trimmed();
		}
	}
	if( transcript.isEmpty() )
	{
		const QString whisperErrors = QString::fromUtf8( whisperProcess.readAllStandardError() ).trimmed();
		appendLog( tr( "Whisper returned no transcript%1" )
			.arg( whisperErrors.isEmpty() ? QString() : QStringLiteral( ": " ) + whisperErrors ) );
		return false;
	}

	appendLog( tr( "Heard: %1" ).arg( transcript ) );
	m_input->setText( transcript );
	runCommand();
	return true;
}

void AgentControlView::voiceProcessError( QProcess::ProcessError error )
{
	if( m_voiceRecordProcess == nullptr )
	{
		return;
	}

	if( error == QProcess::FailedToStart )
	{
		appendLog( tr( "Voice capture failed to start. Ensure %1 is installed." ).arg( ffmpegPath() ) );
	}
}

} // namespace lmms::gui
